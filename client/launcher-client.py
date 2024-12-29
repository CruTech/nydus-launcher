#!/usr/bin/python3

import ssl
import socket
import common
from nydus.client import ClientConfig

MAXMSG = 1024

# Delimiter character used in allocation messages
# and how many of them a complete message will contain
ALLOC_DCHAR = ":"
ALLOC_DELIMS = 3

REQUEST_COMMAND = "REQUEST"
RELEASE_COMMAND = "RELEASE"

NETENC="utf-8"

MSG_END = "\n"


# Entry point of the nydus-launcher client.
# Decide which Minecraft version to launch.
# Use the json files under .minecraft to find all the jars we need.
# Request an account from the server.
# Launch Minecraft using those jars and account details.


def request(ssock):
    
    sys_username = common.get_username()
    request_str = "{} {}\n".format(REQUEST_COMMAND, sys_username)
    request_data = request_str.encode(encoding=NETENC)
    
    total_sent = 0
    while total_sent < len(request_data):
        total_sent += ssock.send(request_data)

    # Note you can be kept waiting for data forever
    # by a rogue server. Add some kind of timeout.
    str_data = ""
    received_count = -1
    while len(str_data) < MAXMSG:
        data = ssock.recv(MAXMSG)
        received_count = len(data)
        str_data += data.decode(encoding=NETENC)

        if MSG_END in str_data:
            break

    num_delims = str_data.count(ALLOC_DCHAR)
    assert num_delims == ALLOC_DELIMS,\
            "Alloc message had incorrect number of delimiters; should have had {} but had {}"\
            .format(ALLOC_DELIMS, num_delims)

    parts = str_data.split(ALLOC_DCHAR)

    ssock.close()

    # Error to handle: some kind of form validity check for each data piece?
    mc_version = parts[0]
    mc_username = parts[1]
    mc_uuid = parts[2]
    mc_token = parts[3]
    print("Got Minecraft version {}".format(mc_version))
    print("Got Minecraft username {}".format(mc_username))
    print("Got Minecraft uuid {}".format(mc_uuid))
    print("Got auth token {}".format(mc_token))


def client_main(cfg):

    context = ssl.create_default_context()

    # Manually add the self signed CA to the trusted store
    # Should we allow this to be configured, or require
    # that the cert be in system trusted store?
    # Error to handle: if cert doesn't exist
    context.load_verify_locations(cafile=cfg.get_ca_cert())

    # Error to handle: server ip not reachable
    # Error to handle: nothing listening on wanted port
    dest_ip = cfg.get_server_ip()
    with socket.create_connection((dest_ip, cfg.get_port())) as sock:
        with context.wrap_socket(sock, server_hostname=dest_ip) as ssock:
           
            request(ssock)


def startup():
    cfg = ClientConfig()
    return cfg

def main():
    cfg = startup()
    client_main(cfg)

main()
