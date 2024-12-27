
import os

IP_SEG_MIN = 0
IP_SEG_MAX = 255
PORT_MIN = 0
PORT_MAX = 2**16 - 1
MC_VERSION_PARTS = 3

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

    if num < 0:
        return False
    return True

"""
Given a string, tells you if the string
represents an integer
"""
def is_integer(num):
    if nu
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