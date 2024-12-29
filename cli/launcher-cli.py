#!/usr/bin/python3

import sys
import validity
from allocater import AllocEngine
from nydus.cli import CliConfig

PROGNAME = "nydus-cli"

VIEW = "view"
VIEW_UUID = "view-uuid"
VIEW_IP = "view-ip"
ALLOC = "alloc"
RELEASE_UUID = "release-uuid"
RELEASE_IP = "release-ip"
CLEANUP = "cleanup"
HELP = "help"
CREATE = "create"

COMMANDS = [
    VIEW,
    VIEW_UUID,
    VIEW_IP,
    ALLOC,
    RELEASE_UUID,
    RELEASE_IP,
    CLEANUP,
    CREATE,
    HELP,
]

SIMPLE_COMMANDS = [
    VIEW,
    CLEANUP,
    HELP,
]

UUID_COMMANDS = [
    VIEW_UUID,
    RELEASE_UUID,
]

IP_COMMANDS = [
    VIEW_IP,
    RELEASE_IP,
]

IP_USER_UUID_COMMANDS = [
    ALLOC,
]

FILE_COMMANDS = [
    CREATE,
]

# The Nydus Cli provides a command line tool
# which you use to interact with the server.
# Primarily this works by modifying the file containing
# account allocations.

# Nydus Cli reads from the same configuration file
# as the Nydus server so that it knows where to find
# the allocation database file.
# But it doesn't store everything in the config file
# since only the location of the allocation file needs
# to be known.

# Operations supported by Nydus Cli:
# - View allocation database; all accounts or search
#   for specific attributes.
# - Manually command the allocation of an account to a
#   particular IP and system username.
# - Manually command the release of accounts identified
#   by uuid.
# - Manually command the release of accounts identified
#   by client IP to which they were allocated.
# - Perform a cleanup of the allocation database, searching
#   for and releasing accounts which have been allocated too long,
#   or which are allocated to IPs/users which are no longer
#   switched on/logged in.
# - Authenticate a list of accounts and generate a new allocation
#   database file from that. The list of accounts will likely
#   be provided as a list of email addresses and then the user
#   will have to manually authenticate each through a browser via password.

def help():
    pass
    exit(0)

def usage():
    print("Usage: {} <com>".format(PROGNAME))
    print("Valid commands are: {}".format(", ".join(COMMANDS)))
    exit(1)

def ip_user_uuid_usage(command):
    assert command in COMMANDS, "Passed '{}' as a command when it's not in the list of valid commands.".format(command)
    print("Usage: {} {} <ip address> <username> <uuid>".format(PROGNAME, command))
    exit(1)

def uuid_usage(command):
    assert command in COMMANDS, "Passed '{}' as a command when it's not in the list of valid commands.".format(command)
    print("Usage: {} {} <uuid>".format(PROGNAME, command))
    exit(1)

def ip_usage(command):
    assert command in COMMANDS, "Passed '{}' as a command when it's not in the list of valid commands.".format(command)
    print("Usage: {} {} <ip address>".format(PROGNAME, command))
    exit(1)

def process_args():
    cmdargs = sys.argv[:1]

    if len(cmdargs) < 1:
        usage()

    command = cmdargs[0]
    if command in COMMANDS:

        if command in SIMPLE_COMMANDS:
            data = ""

        elif command in UUID_COMMANDS:
            if len(cmdargs) < 2:
                uuid_usage(command)
            data = cmdargs[1]
            
            if not validity.is_valid_minecraft_uuid(data):
                uuid_usage(command)

        elif command in IP_COMMANDS:
            if len(cmdargs) < 2:
                ip_usage(command)
            data = cmdargs[1]
            if not validity.is_valid_ipaddr(data):
                ip_usage(command)

        elif command in IP_USER_UUID_COMMANDS:
            if len(cmdargs) < 4:
                ip_user_uuid_usage(command)
            ip = cmdargs[1]
            user = cmdargs[2]
            uuid = cmdargs[3]
            if not validity.is_valid_ipaddr(ip):
                ip_user_uuid_usage(command)
            if not validity.is_valid_system_username(user):
                ip_user_uuid_usage(command)
            if not validity.is_valid_minecraft_uuid(uuid):
                ip_user_uuid_usage(command)

            data = (ip, user, uuid)
    else:
        usage()
    
    return (command, data)

def cli_main(cfg):

    command, data = process_args()

    allocengine = AllocEngine(cfg.get_alloc_file())

    if command == VIEW:
        print(allocengine)
    elif command == VIEW_UUID:
        print(allocengine.view_uuid(data))
    elif command == VIEW_IP:
        print(allocengine.view_ip(data))
    elif command == ALLOC:
        client_ip = data[0]
        client_username = data[1]
        uuid = data[2]
        allocengine.allocate_uuid(uuid, client_ip, client_username)
    elif command == RELEASE_UUID:
        allocengine.release_account_uuid(data)
    elif command == RELEASE_IP:
        allocengine.release_account_ip(data)
    elif command == CREATE:
        pass
    elif command == CLEANUP:
        # TODO
        pass

def startup():
    cfg = CliConfig()
    return cfg

def main():
    cfg = startup()
    cli_main(cfg)

main()
