#!/usr/bin/python3

import socket
import ssl
import random
import datetime
import threading
from nydus.common.allocater import AllocEngine
from nydus.server import ServerConfig
from nydus.common import validity
from nydus.common import netauth
from nydus.common.MCAccount import MCAccount

# TODO cleanup protocol
# Check for accounts which should be de-allocated
# and de-allocate them
# TODO renewal protocol
# Periodically check all the tokens for all the accounts
# and renew them if necessary.

# The lock which controls access to the account allocation file
ALLOCDB_LOCK = threading.Lock()

ALLOC_FILE = "/etc/nydus-launcher/nydus-alloc.csv"

MAXMSG = 1024

# Delimiter character used in allocation messages
# and how many of them a complete message will contain
ALLOC_DCHAR = ":"
ALLOC_DELIMS = 3
ALLOC_BASE = ALLOC_DCHAR.join(["{}"] * (ALLOC_DELIMS+1)) + "\n"

REQUEST_COMMAND = "REQUEST"
RELEASE_COMMAND = "RELEASE"

NETENC = "utf-8"

MSG_END = "\n"

SRV_TIMEOUT = 5

# 30 minutes in seconds
RENEWAL_PERIOD = 30 * 60
RENEWAL_DT = datetime.timedelta(seconds=RENEWAL_PERIOD)


# Entry point to the nydus-launcher server.
# Runs as a daemon which clients connect to.
# Creates threads to allocate accounts.
# Periodically cleans up account allocations in case a client didn't release.
# May also receive commands from the admin on the server.

"""
The master cleanup function which runs every RENEWAL_PERIOD
It renews all authentication tokens which are close to expiring.
It releases all Minecraft account allocations which have passed the
allocation timeout.
For accounts which are still allocated, it checks for whether those client
IPs are still allocated and those system users are still logged in. If not,
the relevant Minecraft account is released.
"""
def cleanup(cfg, app):

    # TODO
    # Does this lock up the allocations for too long?
    # Do we need to split this into multiple
    # separate operations with separate claim/release
    # on the lock?
    with ALLOCDB_LOCK:
        alloc_engine = AllocEngine(cfg.get_alloc_file())

        renew_tokens(cfg, app, alloc_engine)
        alloc_engine.release_expired()
        release_unused_accounts(cfg)

"""
Looks for access tokens in the alloc db which are close to expiring,
and renews them.
"""
def renew_tokens(cfg, app, alloc_engine):
    all_accounts = alloc_engine.get_accounts()
    for acc in all_accounts:

        # We try/except everything here because if one
        # authentication fails we still want to try renewing
        # everything else

        if acc.msal_expired():
            ms_username = acc.get_ms_username()
            try:
                msal_tok = netauth.get_tok_msal(ms_username, app, interactive_allowed=False)
                acc.update_msal_token(msal_tok)
            except Exception:
                pass

        if acc.xboxlive_expired():
            msal_tok = acc.get_msal_at()
            try:
                xboxlive_tok = netauth.get_tok_xboxlive(msal_tok)
                acc.update_xboxlive_token(xboxlive_tok)
            except Exception:
                pass

        if acc.xsts_expired():
            xboxlive_tok = acc.get_xboxlive_at()
            try:
                xsts_tok = netauth.get_tok_xsts(xboxlive_tok)
                acc.update_xsts_token(xsts_tok)
            except Exception:
                pass

        if acc.minecraft_expired():
            xsts_tok = acc.get_xsts_at()
            try:
                minecraft_tok = netauth.get_tok_minecraft(xsts_tok)
                acc.update_minecraft_token(minecraft_tok)

                # The minecraft access token is also in MCAccount
                # so we need to update that too
                mc_username = acc.get_mc_username()
                mc_uuid = acc.get_mc_uuid()
                mc_acc = MCAccount(mc_username, mc_uuid, minecraft_tok.get_token())
                acc.update_minecraft_account(mc_acc)
            except Exception:
                pass


"""
Looks for accounts which are allocated to IP addresses/system users
which aren't in use right now (therefore the Minecraft account
can't be in use) and releases them.
"""
def release_unused_accounts(cfg):
    pass

def allocate_account(cfg, conn, addr, sys_username):
    # Allocate a Minecraft account to that username
    # and that IP address

    client_ip = addr[0]

    version = cfg.get_mc_version()

    with ALLOCDB_LOCK:
        alloc_engine = AllocEngine(cfg.get_alloc_file())
        mc_account = alloc_engine.allocate_one_account(client_ip, sys_username)

    # Error to handle: no account could be obtained
    # TODO what kind of exception?
    if mc_account == None:
        raise Exception("Could not allocate a Minecraft account when requested")
    mc_username = mc_account.get_mc_username()
    mc_uuid = mc_account.get_mc_uuid()
    mc_token = mc_account.get_mc_token()

    allocation_str = ALLOC_BASE.format(version,
            mc_username, mc_uuid, mc_token)

    allocation_data = allocation_str.encode(encoding=NETENC)

    sent_data = 0
    while sent_data < len(allocation_data):
        sent_data += conn.send(allocation_data[sent_data:])

def release_account(cfg, conn, addr):
    # Release the account on that address

    client_ip = addr[0]

    with ALLOCDB_LOCK:
        alloc_engine = AllocEnginge(cfg.get_alloc_file())
        alloc_engine.release_account_ip(client_ip)

def handle_connection(cfg, conn, addr):
    try:
        client_exchange(cfg, conn, addr)
    except TimeoutError:
        print("Client {} took too long to respond".format(addr))

def client_exchange(cfg, conn, addr):

    received_count = -1
    str_data = ""

    # Don't keep receiving data forever
    # We don't want the clients to be able to consume all our memory
    # If they exceed this limit they're doing something wrong anyway.

    recv_start = datetime.datetime.now()
    while len(str_data) < MAXMSG:

        # TODO handle the error if the other side closes early
        new_data = conn.recv(MAXMSG)
        received_count = len(new_data)
        str_data += new_data.decode(encoding=NETENC)

        # A newline character signals end of message
        if MSG_END in str_data:
            break

        now = datetime.datetime.now()
        if now - recv_start > datetime.timedelta(seconds=SRV_TIMEOUT):
            raise TimeoutError("Client took too long to respond")

    # The space is intentional; there should be a space between
    # the REQUEST command and the username
    if str_data.startswith(REQUEST_COMMAND + " "):
        sys_username = str_data[len(REQUEST_COMMAND) + 1:]
        # Check the username exists, something like
        # is_real_system_username(username)
        
        allocate_account(cfg, conn, addr, sys_username)

    elif str_data.startswith(RELEASE_COMMAND):
        
        release_account(cfg, conn, addr)

    else:
        print("Invalid connection from host {}".format(addr))

    conn.close()

"""
Takes in path to file which should have the list of Microsoft accounts
we want to use inside it. Each line of the file should be one Microsoft
account username, and should contain no whitespace.
Returns a list of strings, each string being one of the usernames.
"""
def read_accounts_file(path):
    ms_usernames = []
    with open(path, "r") as f:
        for line in f:
            line = line.rstrip("\n")
            if len(line.split()) != 1:
                raise ValueError("Each line of the accounts file should be a single Microsoft username, but found a line containing whitespace. The file: {}. The line: {}".format(path, line))

            if not validity.is_valid_microsoft_username(line):
                raise ValueError("This line in the accounts file was not a valid Microsoft username: {}".format(line))
            ms_usernames.append(line)
    return ms_usernames


"""
cfg: the ServerConfig instance for use on this server
app: the MSAL PublicClientApplication this server will use in authentication
Gets Microsoft usernames out of the accounts file, attempts to authenticate them,
(interactively; the user needs to manully log accounts in when the server starts)
creates the allocation db file using the accounts which authd successfully.
Returns nothing
"""
def initialise_accounts(cfg, app):
    username_list = read_accounts_file(cfg.get_accounts_file())
    auth_dict = netauth.auth_all(username_list, app, interactive_allowed=True)
    authed_aats = [aat for aat in auth_dict.values() if aat != None]
    failed_aats = [aat for aat in auth_dict.values() if aat == None]
    print("From {} requested Microsoft accounts, the following {} were authenticated.".format(len(username_list), len(authed_aats)))
    for aat in authed_aats:
        print(aat.get_microsoft_username())

    print("The following {} failed authentication.".format(len(failed_aats)))
    for aat in failed_aats:
        print(aat.get_microsoft_username())

    # This is the one instance where no locking is required
    # before running the AllocEngine, because no threads
    # will be spawned until the main server loop is reached.
    alloc_engine = AllocEngine(cfg.get_alloc_file())

    # Create a whole new alloc db only if nothing is already
    # in the file.
    # Otherwise proceed with the file's contents.
    if alloc_engine.num_total_accounts() == 0:
        alloc_engine.create_db(authed_aats)

def startup():
    cfg = ServerConfig()
    return cfg

def server_main(cfg, app):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

    # Error to handle: what if cert file and cert key can't be found/files don't exist/permission denied?
    context.load_cert_chain(cfg.get_cert_file(), cfg.get_cert_privkey())

    # Error to handle: what if desired IP is not on this machine?
    # Error to handle: what if desired port is in use?
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        sock.bind((cfg.get_ip_addr(), cfg.get_port()))
        sock.listen(5)

        with context.wrap_socket(sock, server_side=True) as ssock:
            while True:
                conn, addr = ssock.accept()
                ct = threading.Thread(target=handle_connection, args=(conn, addr))
                ct.start()


def main():
    cfg = startup()
    app = netauth.create_msal_app(cfg.get_msal_cid())
    initialise_accounts(cfg, app)
    server_main(cfg, app)

main()
