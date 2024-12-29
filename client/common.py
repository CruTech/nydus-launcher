#!/usr/bin/python3

"""
Utilities needed in multiple Nydus client modules
"""

import os
import pwd
import re

"""
Raises OSError if something's wrong with pwd database entry
"""
def get_pwd_entry(uid=None):

    if not uid:
        # May raise OSError
        uid = os.getuid()

    try:
        pwdentry = pwd.getpwuid(uid)
    except KeyError:
        raise OSError("Could not find pwd database entry for uid {}.".format(uid))

    if not isinstance(pwdentry, pwd.struct_passwd):
        raise OSError("getpwuid returned a {} instead of a pwd database entry for uid {}.".format(type(pwdentry), uid))

    return pwdentry


"""
Raises OSError if username can't be found for some reason
"""
def get_username():

    pwdentry = get_pwd_entry()

    if not hasattr(pwdentry, "pw_name"):
        raise OSError("pwd database entry for uid {} has no username.".format(uid))

    username = pwdentry.pw_name

    if not isinstance(username, type("")):
        raise OSError("getpwuid for uid {} gave non-string where username should be.".format(uid))

    if username == "":
        raise OSError("getpwuid returned empty string for username of uid {}.".format(uid))

    return username

"""
Raises OSError if home directory can't be found for some reason
"""
def get_home_dir():

    pwdentry = get_pwd_entry()

    expanded_homedir = os.path.expanduser("~")

    if hasattr(pwdentry, "pw_dir"):
        home_dir = pwdentry.pw_dir

    # os.path.expanduser returns the original string if expansion
    # failed
    elif expanded_homedir != "~":
        # Plan B; use os.path's user home directory expansion
        home_dir = expanded_homedir

    else:
        # Plan C; assume standard structure and get username
        username = get_username()
        home_dir = os.path.join("/home", username)

    # We have our prospective home directory
    
    if not isinstance(home_dir, str):
        raise OSError("User's home directory is not a string.")

    if home_dir == "":
        raise OSError("User's home directory is an empty string.")

    if not os.path.isdir(home_dir):
        raise OSError("User's home directory {} does not exist.".format(home_dir))

    return home_dir


"""
Gets path to current user's .minecraft folder (including '.minecraft' in the path)
Raises OSError if it can't be found.
"""
def get_minecraft_path():
    
    home_dir = get_home_dir()

    minecraft_path = os.path.join(home_dir, ".minecraft")

    if not os.path.isdir(minecraft_path):
        raise OSError("User's Minecraft directory does not exist at {}".format(minecraft_path))
    return minecraft_path

"""
Python's default lstrip, given a to_strip string of more than one character,
will strip everything off the original string until it finds a character
which does not appear in the to_strip string at all.
i.e. 'https://thog.com'.lstrip('https://') will return 'og.com', not 'thog.com'
becuase the 't' and 'h' in 'thog' are also characters in 'https://'.
This function strips only the exact to_strip string provided, and doesn't
change the original string if it doesn't start with to_strip.
So strict_lstrip('https://thog.com', 'https://') will return 'thog.com'
and strict_lstrip('https:google', 'ht') will return 'tps:google'
"""
def strict_lstrip(orig, to_strip):
    assert isinstance(orig, str), "non-string provided as orig to strict_lstrip: {}".format(orig)
    assert isinstance(to_strip, str), "non-string provided as to_strip to strict_lstrip: {}".format(to_strip)

    if not orig.startswith(to_strip):
        return orig

    new = orig[len(to_strip):]
    return new

"""
strict_rstrip is to rstrip as strict_lstrip is to lstrip
"""
def strict_rstrip(orig, to_strip):
    assert isinstance(orig, str), "non-string provided as orig to strict_rstrip: {}".format(orig)
    assert isinstance(to_strip, str), "non-string provided as to_strip to strict_rstrip: {}".format(to_strip)

    if not orig.endswith(to_strip):
        return orig

    new = orig[:len(orig) - len(to_strip)]
    return new

"""
We expect url is https, and ends in a file path, since that seems to be the case
for all urls indicating files to download
TODO Should we do this with a regex?
"""
def is_download_url(url):

    assert isinstance(url, str), "non-string provided as url to is_download_url: {}".format(url)

    protocol = "https://"

    if not url.startswith(protocol):
        # Not https
        return False

    without_protocol = strict_lstrip(url, protocol)

    slash_idx = without_protocol.find("/")
    if slash_idx < 0:
        # No file path
        return False

    domain = without_protocol[:slash_idx]
    path = without_protocol[slash_idx + 1:]

    if len(domain) < 1:
        return False

    if len(path) < 1:
        return False
    
    return True

"""
If the url conforms to is_download_url, returns the domain
"""
def get_url_domain(url):
    assert is_download_url(url), "url provided to get_url_domain is not a download url: {}".format(url)
    protocol = "https://"
    without_protocol = strict_lstrip(url, protocol)

    slash_idx = without_protocol.find("/")
    if slash_idx < 0:
        # No file path
        raise ValueError("url {} did not have a file path despite passing the check for being a download url")

    domain = without_protocol[:slash_idx]
    path = without_protocol[slash_idx + 1:]
    return domain

"""
If the url conforms to is_download_url, returns the path
"""
def get_url_path(url):
    assert is_download_url(url), "url provided to get_url_path is not a download url: {}".format(url)
    protocol = "https://"
    without_protocol = strict_lstrip(url, protocol)

    slash_idx = without_protocol.find("/")
    if slash_idx < 0:
        # No file path
        raise ValueError("url {} did not have a file path despite passing the check for being a download url")

    path = without_protocol[slash_idx + 1:]
    return path

"""
sha1 hash digests appearing in the Minecraft json files
are presented as 40 hexadecimal digits
digest: a string
Returns True if the digest is the right form for a sha1 hash
False otherwise
"""
def is_sha1(digest):
    assert isinstance(digest, str), "sha1 digest given was not a string: {}".format(digest)

    if re.fullmatch(r"[0-9a-f]{40}", digest):
        return True
    return False

if __name__ == "__main__":
    print(get_minecraft_path())
