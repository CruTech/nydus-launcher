#!/usr/bin/python3

from NydusConfig import NydusConfig

SERVER_CONFIG_FILE = "/etc/nydus-launcher/server.conf"

SERVER_CONFIG_DICT = {
    "IpAddr": "192.168.1.1"
    "Port": "2011"
    "CertFile": "nydus-server.crt"
    "CertPrivKey": "nydus-server.key"
}

# Entry point to the nydus-launcher server.
# Runs as a daemon which clients connect to.
# Forks off those connections to allocate accounts.
# Periodically cleans up account allocations in case a client didn't release.
# May also receive commands from the admin on the server.

def startup():
    cfg = NydusConfig(SERVER_CONFIG_FILE, SERVER_CONFIG_DICT)
    return cfg

