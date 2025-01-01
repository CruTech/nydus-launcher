
import os
import datetime
import pwd

IP_SEG_MIN = 0
IP_SEG_MAX = 255
PORT_MIN = 0
PORT_MAX = 2**16 - 1
MC_VERSION_PARTS = 3
TIME_FORMAT = "%d-%m-%Y %H:%M:%S"
XB_EXPIRY_SECONDS_FORMAT = "%Y-%m-%dT%H:%M:%S"
XB_EXPIRY_FORMAT = XB_EXPIRY_SECONDS_FORMAT + "%fZ"
XB_EXPIRY_SUFFIX = "Z"
XB_EXPIRY_SEPARATER = "."

"""
Returns True if
1. the given string is a file, and
2. the file exists, and
3. we have permission to read it
Return False otherwise
"""
def is_valid_file(filename):
    if not isinstance(filename, str):
        return False

    if os.path.isfile(filename):
        try:
            with open(fname, "r") as f:
                pass
        except PermissionError:
            return False
    return True

"""
This function is designed for conventional
representation of IPv4 only.
Returns True if the string is a valid IPv4
address, False otherwise.
"""
def is_valid_ipaddr(ipaddr):
    if not isinstance(ipaddr, str):
        return False

    parts = ipaddr.split(".")
    if len(parts) != 4:
        return False

    for seg in parts:
        if not is_limited_integer(seg, IP_SEG_MIN, IP_SEG_MAX):
            return False
    return True

"""
Returns True if given string is a valid port number
False otherwise
Ports are numbers between 0 and 2^16-1
"""
def is_valid_port(port):
    if not isinstance(port, str):
        return False

    return is_limited_integer(port, PORT_MIN, PORT_MAX)

"""
Given a string, tells you if the string
represents an integer within the boundaries
you define
"""
def is_limited_integer(num, min_val, max_val):
    assert isinstance(min_val, int), "Min val of integer limit must be an integer"
    assert isinstance(max_val, int), "Max val of integer limit must be an integer"
    if not is_integer(num):
        return False
    num = int(num)

    if num < min_val or num > max_val:
        return False
    return True

"""
Given a string, tells you if the string
represents a positive integer
"""
def is_positive_integer(num):
    if not is_integer(num):
        return False
    num = int(num)

    if num <= 0:
        return False
    return True

"""
Given a string, tells you if the string
represents an integer
"""
def is_integer(num):
    if not num.isdecimal():
        return False
    try:
        num = int(num)
    except:
        return False
    return True

"""
Returns True if the given string is a valid
Minecraft version. False otherwise.
TODO
Requires work.
The general form of X.Y.Z is easy to test for,
but there are pre-release versions too, and OptiFine
is its own kind of Minecraft version.
We can't just define a valid Minecraft version based
on the existence of a json file; this function will
first be used on the server where the json files
haven't been downloaded.
"""
def is_valid_minecraft_version(vers):
    if not isinstance(vers, str):
        return False
    parts = vers.split(".")
    if len(parts) != MC_VERSION_PARTS:
        return False
    
    for seg in parts:
        if not is_positive_integer(seg):
            return False
    return True

# TODO
# More precise checks for valid username, uuid,
# and access token, and msal cid
# Need to know the exact rules.
def is_valid_minecraft_username(acc):
    if not is_nonempty_str(acc):
        return False
    return True

def is_valid_minecraft_uuid(uuid):
    if not is_nonempty_str(uuid):
        return False
    return True

def is_valid_minecraft_token(token):
    if not is_nonempty_str(token):
        return False
    return True

def is_valid_msal_cid(cid):
    if not is_nonempty_str(cid):
        return False
    return True

def is_valid_msal_token(token):
    if not is_nonempty_str(token):
        return False
    return True

def is_valid_xboxlive_token(token):
    if not is_nonempty_str(token):
        return False
    return True

def is_valid_xsts_token(token):
    if not is_nonempty_str(token):
        return False
    return True

def is_nonempty_str(mystr):
    if not isinstance(mystr, str):
        return False
    if len(mystr) == 0:
        return False
    return True

"""
This function validates that a given string
is in the correct form to represent a timestamp,
not that the given item is itself a datetime
object.
This is in reference to the standard timestamp
format used internally in nydus launcher code,
not the timestamp formats used by external entities
the nydus launcher interacts with.
"""
def is_valid_str_timestamp(ts):
    if not is_nonempty_str(ts):
        return False

    try:
        dt = datetime.datetime.strptime(ts, TIME_FORMAT)
    except ValueError:
        return False
    return True

"""
This function validates that a given string
is in the format used by Xbox authentication
endpoints to represent a timestamp (mainly
used for token expiry timestamps).
The format includes a fractional part for
seconds which may be 6 or 7 digits, and
therefore is not easily parsed by datetime.
"""
def is_valid_xbox_timestamp(ts):
    if not is_nonempty_str(ts):
        return False
    
    parts = ts.split(XB_EXPIRY_SEPARATER)
    if not (len(parts) == len(XB_EXPIRY_FORMAT.split(XB_EXPIRY_SEPARATER)) == 2):
        return False
    
    seconds_part = parts[0]
    fractional_part = parts[1]

    try:
        datetime.datetime.strptime(seconds_part, XB_EXPIRY_SECONDS_FORMAT)
    except ValueError:
        return False

    if not fractional_part.endswith(XB_EXPIRY_SUFFIX):
        return False

    fractional_part = fractional_part.rstrip(XB_EXPIRY_SUFFIX)
    if len(fractional_part) < 6 or len(fractional_part) > 7:
        return False

    if not fractional_part.is_decimal():
        return False

    return True

# Check list of system users
def is_valid_system_username(username):
    if not is_nonempty_str(username):
        return False
    
    try:
        pwdentry = pwd.getpwdnam(username)
    except KeyError:
        return False
    
    return True

# TODO what's a valid Microsoft username? An email address?
def is_valid_microsoft_username(username):
    if not is_nonempty_str(username):
        return False
    return True

"""
A 'parname' or 'parameter name' is the name of a configuration
parameter as found in a config file used by some part of the Nydus launcher.
Parnames must be strings and must not contain an equals sign
or any whitespace.
"""
def is_valid_parname(parname):
    if not isinstance(parname, str):
        return False
    if parname.find("=") != -1:
        return False
    if len(parname.split()) > 1:
        return False
    return True

"""
Checks for the given object being a list
of valid parnames.
"""
def is_valid_parnames(parnames):
    if not isinstance(parnames, list):
        return False
    for p in parnames:
        if not is_valid_parname(p):
            return False
    return True

"""
A 'defconfig' is a dictionary where the keys are parnames
and the values are default values for those parameters.
"""
def is_valid_defconfig(defconfig):
    if not isinstance(defconfig, dict):
        return False
    if not is_valid_parnames(defconfig.keys()):
        return False
    for k in defconfig:
        if not isinstance(defconfig[k], str):
            return False
    return True

"""
A 'varname' is the name of a class attribute under which
the value of a config parameter will be stored.
It must be
1) a string
2) a valid python identified
3) not overlap with any existing Nydus Config class attributes
"""
def is_valid_varname(varname)
    if not isinstance(varrname, str):
        return False
    if not varname.isidentifier():
        return False

    nydus_config_reserved = ["path", "parnames", "varnames"]
    if varname in nydus_config_reserved:
        return False
    return True

"""
A 'varnames' is a dictionary where the keys are parnames
and the values are class attribute names which will store
the value of those parameters.
That is, the value must be a valid python identifier.
"""
def is_valid_varnames(varnames):
    if not isinstance(varnames, dict):
        return False
    if not is_valid_parnames(varnames.keys()):
        return False
    for k in varnames:
        attrname = varnames[k]
        if not is_valid_varname(attrname):
            return False
    return True
