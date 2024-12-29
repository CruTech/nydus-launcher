#!/usr/bin/python3

import socket
import ssl
import random
import datetime
import threading
from allocater import AllocEngine
from nydus.server import ServerConfig

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


# Entry point to the nydus-launcher server.
# Runs as a daemon which clients connect to.
# Forks off those connections to allocate accounts.
# Periodically cleans up account allocations in case a client didn't release.
# May also receive commands from the admin on the server.

"""
Generates random strings of given length.
Strings may contain upper and lower case letters, and numbers
There will be no symbols
strlen: int, exact length of string to generate
"""
def randomstring(strlen):
    assert isinstance(strlen, int), "Must specify length of random string as an integer"
    assert strlen > 0, "strlen of random string must be positive"
    alpha = "abcdefghijklmnopqrstuvwxyz"
    number = "1234567890"

    allchars = alpha + alpha.upper() + number

    out = "".join([random.choice(allchars) for i in range(strlen)])
    return out

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

def startup():
    cfg = ServerConfig()
    return cfg

def server_main(cfg):
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
    server_main(cfg)

main()
