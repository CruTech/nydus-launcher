
import os

IP_SEG_MIN = 0
IP_SEG_MAX = 255
PORT_MIN = 0
PORT_MAX = 2**16 - 1

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
        if not seg.isdecimal():
            return False
        num = int(seg)
        if not IP_SEG_MIN <= num <= IP_SEG_MAX:
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

    if not port.isdecimal():
        return False

    port = int(port)
    if not PORT_MIN <= port <= PORT_MAX:
        return False
    return True
