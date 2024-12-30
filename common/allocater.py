#!/usr/bin/python3

import datetime
import os
from nydus.common.validity import TIME_FORMAT
from nydus.common.MCAccount import MCAccount
from nydus.common.AccessToken import AccessToken
from nydus.common.AccountAuthTokens import AccountAuthTokens

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

FIELDS = [
    "client_ip",
    "client_username",
    "alloc_time",
    "ms_username",
    "msal_token",
    "msal_expiry",
    "xboxlive_token",
    "xboxlive_expiry",
    "xsts_token",
    "xsts_expiry",
    "xsts_hash",
    "mc_token",
    "mc_expiry",
    "mc_username",
    "mc_uuid",
]

"""
Represents one line of the account allocation
database file.
The alloc_time and token_time attributes store
datetime objects, but you should pass a string, not a datetime,
to the constructor for those fields.
"""
class AllocAccount:

    """
    Constructor accepts all the fields individually.
    It's intended to receive data direct from the allocation file.
    Order of parameters to constructor must be same as order of
    parameters in allocation file.
    If you've independently created an AccountAuthTokens instance
    and want to use that directly, call the class method
    AllocAccount.create_from_aat()
    """
    def __init__(self, client_ip, client_username, alloc_time,
            ms_username, msal_token, msal_expiry, xboxlive_token,
            xboxlive_expiry, xsts_token, xsts_expiry, xsts_hash,
            mc_token, mc_expiry, mc_username, mc_uuid):

        self.set_client_ip(client_ip)
        self.set_client_username(client_username)
        self.set_alloc_time(alloc_time)

        msal_at = AccessToken(msal_token, msal_expiry)
        xbl_at = AccessToken(xboxlive_token, xboxlive_expiry)
        xsts_at = AccessToken(xsts_token, xsts_expiry, xsts_hash)
        mc_at = AccessToken(mc_token, mc_expiry)
        mc_acc = MCAccount(mc_username, mc_uuid, mc_token)
        aat = AccountAuthTokens(ms_username, msal_at, xbl_at, xsts_at, mc_at, mc_acc)

        self.set_account_auth_tokens(aat)


    def num_fields():
        return len(FIELDS)

    """
    Creates a new AllocAccount with the data you've passed it.
    In particular, it accepts a finished AccountAuthTokens instance
    rather than requiring all data points individually as the
    constructor does.
    Mainly for use when all users are newly authenticated and
    the allocation file is being created for the first time.
    Note that even though you pass in an AccountAuthTokens,
    a new one will be created due to the nature of the AllocAccount
    constructor which is called internally.
    """
    def create_from_aat(client_ip, client_username, alloc_time, aat):

        if not isinstance(aat, AccountAuthTokens):
            raise TypeError("To create an AllocAccount using AccountAuthTokens, an AccountAuthTokens instance must be provided. Instead, {} was given.".format(type(aat)))

        return AllocAccount(
            client_ip,
            client_username,
            alloc_time,
            aat.get_microsoft_username(),
            aat.get_msal_token().get_token(),
            aat.get_msal_token().get_expiry(),
            aat.get_xboxlive_token().get_token(),
            aat.get_xboxlive_token().get_expiry(),
            aat.get_xsts_token().get_token(),
            aat.get_xsts_token().get_expiry(),
            aat.get_xsts_token().get_hash(),
            aat.get_minecraft_token().get_token(),
            aat.get_minecraft_token().get_expiry(),
            aat.get_minecraft_account().get_username(),
            aat.get_minecraft_account().get_uuid(),
        )

    """
    Creates the header line to go in the top of the allocation
    database file.
    Does not include a newline on the end
    """
    def make_header():
        return ALLOC_DELIM.join(FIELDS)

    def copy(self):
        return AllocAccount(
            self.get_client_ip(),
            self.get_client_username(),
            self.get_alloc_time(),
            self.get_account_auth_tokens().copy(),
        )

    """
    There should not be accounts which have only some of the first
    3 fields filled but not all. However, if such accounts exist,
    we count them as unallocated because clearly the allocation
    process broke somehow.
    """
    def is_allocated(self):
        if self.client_ip and self.client_username and self.alloc_time:
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

    # Type checks for the 'update' methods
    # occur inside the AccountAuthTokens method where applicable
    # Use the 'update' methods to replace tokens when one
    # has been renewed.

    def update_msal_token(self, new_msal_token):
        self.aat.set_msal_token(new_msal_token)

    def update_xboxlive_token(self, new_xbl_token):
        self.aat.set_xboxlive_token(new_xbl_token)

    def update_xsts_token(self, new_xsts_token):
        self.aat.set_xsts_token(new_xsts_token)

    def update_minecraft_token(self, new_mc_token):
        self.aat.set_minecraft_token(new_mc_token)

    def update_minecraft_account(self, new_mc_account):
        self.aat.set_minecraft_account(new_mc_account)

    def alloc_expired(self):
        now = datetime.datetime.now()
        if now - self.get_alloc_timeout() > ALLOC_TIMEOUT:
            return True
        return False

    def msal_expired(self):
        return self.aat.get_msal_token().is_expired()

    def xboxlive_expired(self):
        return self.aat.get_xboxlive_token().is_expired()

    def xsts_expired(self):
        return self.aat.get_xsts_token().is_expired()

    def minecraft_expired(self):
        return self.aat.get_minecraft_token().is_expired()

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

    def set_account_auth_tokens(self, aat):
        if isinstance(aat, AccountAuthTokens):
            self.aat = aat
        else:
            raise TypeError("Object given is not an AccountAuthTokens class: {}".format(aat))

    def get_client_ip(self):
        return self.client_ip

    def get_client_username(self):
        return self.client_username

    def get_alloc_time(self):
        return self.alloc_time

    def get_account_auth_tokens(self):
        return self.aat

    def get_ms_username(self):
        return self.aat.get_ms_username()

    """
    Specifically the token string, not the AccessToken object
    """
    def get_msal_token(self):
        return self.aat.get_msal_token().get_token()

    def get_msal_expiry(self):
        return self.aat.get_msal_token().get_expiry()

    """
    Specifically the token string, not the AccessToken object
    """
    def get_xboxlive_token(self):
        return self.aat.get_xboxlive_token().get_token()

    def get_xboxlive_expiry(self):
        return self.aat.get_xboxlive_token().get_expiry()

    """
    Specifically the token string, not the AccessToken object
    """
    def get_xsts_token(self):
        return self.aat.get_xsts_token().get_token()

    def get_xsts_expiry(self):
        return self.aat.get_xsts_token().get_expiry()

    def get_xsts_hash(self):
        return self.aat.get_xsts_token().get_hash()

    """
    Specifically the token string, not the AccessToken object
    """
    def get_mc_token(self):
        return self.aat.get_minecraft_token().get_token()

    def get_mc_expiry(self):
        return self.aat.get_minecraft_token().get_expiry()

    def get_mc_username(self):
        return self.aat.get_minecraft_account().get_username()

    def get_mc_uuid(self):
        return self.aat.get_minecraft_account().get_uuid()

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
            self.get_ms_username(),
            self.get_msal_token(),
            self.get_msal_expiry(),
            self.get_xboxlive_token(),
            self.get_xboxlive_expiry(),
            self.get_xsts_token(),
            self.get_xsts_expiry(),
            self.get_mc_token(),
            self.get_mc_expiry(),
            self.get_mc_username(),
            self.get_mc_uuid(),
        ]

        assert len(fields) == self.num_fields()
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

    def __repr__(self):
        return AllocEngine.list_to_string(self.accounts)

    """
    Given a list of AllocAccount objects, creates a string
    consisting of lines. The first line is the header for AllocAccount fields,
    all other lines represent the accounts in the provided list.
    The string is returned.
    """
    def list_to_string(acclist):
        assert isinstance(acclist, list), "Provided object must be a list of AllocAccounts. Was {}".format(acclist)
        for elem in acclist:
            assert isinstance(elem, AllocAccount), "Provided object must be a list of AllocAccounts. Contained an element '{}'".format(elem)
        outstr = ""
        outstr += "{}\n".format(AllocAccount.make_header())
        for acc in acclist:
            outstr += "{}\n".format(acc)
        return outstr

    def view_uuid(self, uuid):
        if not validity.is_valid_minecraft_uuid(uuid):
            raise ValueError("Not a valid Minecraft uuid: {}".format(uuid))

        to_view = [acc for acc in self.accounts if acc.get_mc_uuid() == uuid]
        return AllocEngine.list_to_string(to_view)

    def view_ip(self, client_ip):
        if not validity.is_valid_ipaddr(client_ip):
            raise ValueError("Not a valid IP address: {}".format(client_ip))

        to_view = [acc for acc in self.accounts if acc.get_client_ip() == client_ip]
        return AllocEngine.list_to_string(to_view)

    def write_changes(self):
        with open(path, "w") as f:
            f.write(str(self))
            f.flush()

    def load_alloc_db(self):
        with open(path, "r") as f:

            first_line = True
            for line in f:

                # Skip first line, since it contains the header for each column
                if first_line:
                    continue

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

        if not validity.is_valid_system_username(client_username):
            raise ValueError("Client username was not a valid system username: {}".format(client_username))

        # Release everything currently allocated to this client
        for acc in self.accounts:
            if acc.is_allocated() and acc.get_client_ip() == client_ip:
                acc.release()

        for acc in self.accounts:
            if not acc.is_allocated():
                acc.allocate(client_ip, client_username)
                self.write_changes()
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
                if acc.is_allocated() and acc.get_mc_uuid() == uuid]

        for acc in to_release:
            acc.release()
        self.write_changes()

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
        self.write_changes()
    
    """
    Finds an account (or all accounts if there are more than one) of a specific
    uuid, and allocates them to the given client IP address and system username
    Overwrites existing allocation of the account(s) in question.
    """
    def allocate_uuid(self, uuid, client_ip, client_username):
        if not validity.is_valid_ipaddr(client_ip):
            raise ValueError("Client IP was not a valid IP address: {}".format(client_ip))

        if not validity.is_valid_system_username(client_username):
            raise ValueError("Client username was not a valid system username: {}".format(client_username))

        if not validity.is_valid_minecraft_uuid(uuid):
            raise ValueError("Not a valid Minecraft uuid: {}".format(uuid))

        to_allocate = [acc for acc in self.accounts\
                if acc.get_mc_uuid() == uuid]

        for acc in to_allocate:
            acc.allocate(client_ip, client_username)

        self.write_changes()
