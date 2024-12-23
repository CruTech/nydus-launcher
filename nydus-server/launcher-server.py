#!/usr/bin/python3

import socket
import ssl
import random
import datetime
import threading
from NydusServerConfig import NydusServerConfig

SERVER_CONFIG_FILE = "/etc/nydus-launcher/server.conf"

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

def allocate_account(conn, addr, sys_username):
    # Allocate a Minecraft account to that username
    # and that IP address

    version = cfg[MCVERSION]
    mc_account = get_next_account()
    mc_username = mc_account.get_username()
    mc_uuid = mc_account.get_uuid()
    mc_token = mc_account.get_token()

    allocation_str = ALLOC_BASE.format(version,
            mc_username, mc_uuid, mc_token)

    allocation_data = allocation_str.encode(encoding=NETENC)

    print("Server started sending")
    sent_data = 0
    while sent_data < len(allocation_data):
        sent_data += conn.send(allocation_data[sent_data:])
    print("server finished sending")

def release_account(conn, addr):
    # Release the account on that address
    print("Released account from host {}".format(addr))

def handle_connection(conn, addr):
    try:
        client_exchange(conn, addr)
    except TimeoutError:
        print("Client {} took too long to respond".format(addr))

def client_exchange(conn, addr):

    print("Server started receiving")
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

    print("Server finished receiving")

    # The space is intentional; there should be a space between
    # the REQUEST command and the username
    if str_data.startswith(REQUEST_COMMAND + " "):
        sys_username = str_data[len(REQUEST_COMMAND) + 1:]
        # Check the username exists, something like
        # is_real_system_username(username)
        
        allocate_account(conn, addr, sys_username)

    elif str_data.startswith(RELEASE_COMMAND):
        
        release_account(conn, addr)

    else:
        print("Invalid connection from host {}".format(addr))

    conn.close()

def startup():
    cfg = NydusServerConfig(SERVER_CONFIG_FILE)
    return cfg

def server_main(cfg):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cfg[CERTFILE], cfg[CERTPRIVKEY])

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        sock.bind((cfg[IPADDR], cfg[PORT]))
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
