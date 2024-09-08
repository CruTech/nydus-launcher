#!/usr/bin/python3

# Entry point to the nydus-launcher server.
# Runs as a daemon which clients connect to.
# Forks off those connections to allocate accounts.
# Periodically cleans up account allocations in case a client didn't release.
# May also receive commands from the admin on the server.
