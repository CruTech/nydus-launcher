#!/usr/bin/python3

import datetime
import os

# Decides which account to give to a client requesting an account.
# Stores the currently allocated accounts in a file.
# Locking blocks race conditions, since each client request threads off the
# main daemon.
# Also handles releasing account allocations by checking for signs a client
# is no longer using that Minecraft account.


# The allocation file uses csv (is there any reason for csv to be
# a problem? Any case where a comma might appear in one of the fields?
# if so we can use tab separated values instead

# Structure is
# client_ip, client_user, time_allocated, username, uuid, access_token, token_time

# That is
# Ip address of the client to which this account has been allocated
# System user who was logged into the machine to which this account was allocated
# Time the allocation was done
# Minecraft account username
# Minecraft account uuid
# Minecraft account access token
# Time at which the access token was aquired

# The first three fields will be empty for unallocated accounts

# The file will be used for

# 1) Account allocation
# read the file, look for an account with first three fields blank,
# write the client IP, client user, and current time in there
# Note one client can only have one account allocated at a time.
# When you allocate one account to a client, also release all others
# allocated to them.

# 2) Account release
# if a client sends a release signal, look through the file for
# all accounts allocated to that client and erase their client IP,
# client user, and alloc time.

# 3) Cleanup
# read through the file
# Release all accounts which
#   - have been allocated more than 2 hours
#   - the user to which they were allocated is no longer logged in on that client
#     (find out using process list since logins are over ssh)
#   - the client to which they were allocated is no longer active
#     (find out using ping or if that address is no longer DHCP allocated)

# 4) Renewal
# Use the msal process to get a new access token and replace the old token
# with the new one.
# This needs to happen periodically. How often?

ALLOC_FILE = "nydus-alloc.csv"

ALLOC_DELIM = ","

# How long an account allocation lasts before
# it will be deleted
ALLOC_TIMEOUT = datetime.timedelta(hours=2)

# How long an access token should be kept
# before getting a new one.
TOKEN_TIMEOUT = datetime.timedelta(hours=12)

TIME_FORMAT = "%d-%m-%Y %H:%M:%S"

"""
Represents one line of the account allocation
database file.
The alloc_time and token_time attributes store
datetime objects, but you should pass a string, not a datetime,
to the constructor for those fields.
"""
class AllocAccount:
    def __init__(self, client_ip, client_username, alloc_time,
            mc_username, mc_uuid, mc_token, token_time):

        self.set_client_ip(client_ip)
        self.set_client_username(client_username)
        self.set_alloc_time(alloc_time)
        self.set_mc_username(mc_username)
        self.set_mc_uuid(mc_uuid)
        self.set_mc_token(mc_token)
        self.set_token_time(token_time)

    def num_fields():
        return 7

    """
    There should not be accounts which have only some of the first
    3 fields filled but not all. However, if such accounts exist,
    we count them as unallocated because clearly the allocation
    process broke somehow.
    """
    def is_allocated(self):
        if client_ip and client_username and alloc_time:
            return True
        return False

    def allocate(self, client_ip, client_username):
        now = datetime.datetime.now()
        now_str = now.strftime(TIME_FORMAT)
        self.set_client_ip(client_ip)
        self.set_client_username(client_username)
        self.set_alloc_time(now_str)

    def release(self):
        self.set_client_ip("")
        self.set_client_username("")
        self.set_alloc_time("")

    """
    This method only renews the username, uuid, token, and
    'last renewed' timestamp as given to it.. The procedure of actually
    legitimately acquiring a new token has to be handled elsewhere.
    """
    def renew(self, new_username, new_uuid, new_token):
        now = datetime.datetime.now()
        now_str = now.strftime(TIME_FORMAT)
        self.set_mc_username(new_username)
        self.set_mc_uuid(new_uuid)
        self.set_mc_token(new_token)
        self.set_token_time(now_str)

    def past_alloc_timeout(self):
        now = datetime.datetime.now()
        if now - self.get_alloc_timeout() > ALLOC_TIMEOUT:
            return True
        return False

    def past_token_timeout(self):
        now = datetime.datetime.now()
        if now - self.get_token_timeout() > TOKEN_TIMEOUT:
            return True
        return False
    
    def set_client_ip(self, client_ip):
        if validator.is_valid_ipaddr(client_ip):
            self.client_ip = client_ip
        else:
            raise ValueError("Client IP value is not a valid IP address: {}".format(client_ip))

    def set_client_username(self, client_username):
        if validator.is_valid_system_username(client_username):
            self.client_username = client_username
        else:
            raise ValueError("Client username value is not a valid system username: {}".format(client_username))

    def set_alloc_time(self, alloc_time):
        if validator.is_valid_str_timestamp(alloc_time):
            self.alloc_time = datetime.datetime.strptime(alloc_time, TIME_FORMAT)
        else:
            raise ValueError("Alloc time value is not a valid timestamp: {}".format(alloc_time))

    def set_mc_username(self, mc_username):
        if validator.is_valid_minecraft_username(mc_username):
            self.mc_username = mc_username
        else:
            raise ValueError("Minecraft username value is not a valid minecraft username: {}".format(mc_username))

    def set_mc_uuid(self, mc_uuid):
        if validator.is_valid_minecraft_uuid(mc_uuid):
            self.mc_uuid = mc_uuid
        else:
            raise ValueError("Minecraft uuid value is not a valid minecraft uuid: {}".format(mc_uuid))

    def set_mc_token(self, mc_token):
        if validator.is_valid_minecraft_token(mc_token):
            self.mc_token = mc_token
        else:
            raise ValueError("Minecraft token value is not a valid minecraft token: {}".format(mc_token))

    def set_token_time(self, token_time):
        if validate.is_valid_str_timestamp(token_time):
            self.token_time = datetime.datetime.strptime(token_time, TIME_FORMAT)
        else:
            raise ValueError("Token renewal time value is not a valid timestamp: {}".format(token_time))

    def get_client_ip(self):
        return self.client_ip

    def get_client_username(self):
        return self.client_username

    def get_alloc_time(self):
        return self.alloc_time

    def get_mc_username(self):
        return self.mc_username

    def get_mc_uuid(self):
        return self.mc_uuid

    def get_mc_token(self):
        return self.mc_token

    def get_token_time(self):
        return self.token_time

    """
    Creates a line of data, suitable for writing back into
    the account allocation database file.
    Does NOT include a newline on the end.
    """
    def __repr__(self):
        fields = [
            self.get_client_ip(),
            self.get_client_username(),
            self.get_alloc_time(),
            self.get_mc_username(),
            self.get_mc_uuid(),
            self.get_mc_token(),
            self.get_token_time(),
        ]
        return ALLOC_DELIM.join(fields)

"""
Initiate the AllocEngine with the path to the csv containing all
the Minecraft accounts
This class is intended to be created again by each thread that
needs to work with the account database, then call one
of its methods to do one of the operations.
"""
class AllocEngine:

    def __init__(self, path):
        if not isinstance(path, str):
            raise TypeError("Path to accounts database file must be a string. Was {}".format(path))

        if not os.path.isfile(path):
            raise FileNotFoundError("Path to accounts database file must exist. Was {}".format(path))

        try:
            with open(path, "r+") as f:
                pass
        except PermissionError:
            raise PermissionError("Accounts database file was not readable. Given path is {}".format(path))
        
        self.path = path
        self.accounts = []
        self.load_alloc_db()

    def load_alloc_db(self):
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                parts = line.split(ALLOC_DELIM)
                if len(parts) != AllocAccount.num_fields():
                    raise ValueError("Line in account allocation database was invalid. It should have had {} {}-separated elements, but had {}. Line looked like: {}".format(AllocAccount.num_fields(), ALLOC_DELIM, len(parts), line))
                
                # Note: this instantiation depends on the order of fields
                # being the same in the db file and in the Account class
                # constructor
                acc = AllocAccount(*parts)
                self.accounts.append(acc)

    """
    If an unallocated account is found, marks it allocated and
    returns the object representing it.
    If no unallocated account is found, returns None.
    
    Always deallocates all accounts currently allocated to this client IP
    """
    def allocate_one_account(self, client_ip, client_username):

        if not validity.is_valid_ipaddr(client_ip):
            raise ValueError("Client IP was not a valid IP address: {}".format(client_ip))

        if not validify.is_valid_system_username(client_username):
            raise ValueError("Client username was not a valid system username: {}".format(client_username))

        # Release everything currently allocated to this client
        for acc in self.accounts:
            if acc.is_allocated() and acc.get_client_ip() == client_ip:
                acc.release()

        for acc in self.accounts:
            if not acc.is_allocated():
                acc.allocate(client_ip, client_username)
                return acc
        return None

    """
    Finds account by uuid
    If the account is found and currently allocated, releases it
    Note that if (somehow) two lines have the same account uuid,
    both will be released.
    """
    def release_account_uuid(self, uuid):
        if not validity.is_valid_minecraft_uuid(uuid):
            raise ValueError("Not a valid Minecraft uuid: {}".format(uuid))

        to_release = [acc for acc in self.accounts\
                if acc.is_allocated() and acc.get_uuid() == uuid]

        for acc in to_release:
            acc.release()

    """
    Finds all accounts allocated to the given client IP
    and releases them.
    """
    def release_account_ip(self, client_ip):
        if not validity.is_valid_ipaddr(client_ip):
            raise ValueError("Not a valid IP address: {}".format(client_ip))

        to_release = [acc for acc in self.accounts \
                if acc.is_allocated() and acc.get_client_ip() == client_ip]

        for acc in to_release:
            acc.release()
            
    
