#!/usr/bin/python3

# Utilities needed in multiple Nydus client modules

import os
import pwd

# Raises OSError if something's wrong with pwd database entry
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


# Raises OSError if username can't be found for some reason
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

# Raises OSError if home directory can't be found for some reason
def get_home_dir():

    pwdentry = get_pwd_entry()

    if hasattr(pwdentry, "pw_dir"):
        home_dir = pwdentry.pw_dir

    else:
        # Plan B; assume standard structure and get username
        username = get_username()
        home_dir = "/home/{}".format(username)

    # We have our prospective home directory
    
    if not isinstance(home_dir, type("")):
        raise OSError("User's home directory is not a string.")

    if home_dir == "":
        raise OSError("User's home directory is an empty string.")

    if not os.is_dir(home_dir):
        raise OSError("User's home directory {} does not exist.".format(home_dir))

    return home_dir


# Gets path to current user's .minecraft folder (including '.minecraft' in the path)
# Raises OSError if it can't be found.
def get_minecraft_path():
    
    home_dir = get_home_dir()

    minecraft_path = "{}/.minecraft".format(home_dir)

    if not os.is_dir(minecraft_path):
        raise OSError("User's Minecraft directory does not exist at {}".format(minecraft_path))

# Python's default lstrip, given a to_strip string of more than one character,
# will strip everything off the original string until it finds a character
# which does not appear in the to_strip string at all.
# i.e. 'https://thog.com'.lstrip('https://') will return 'og.com', not 'thog.com'
# becuase the 't' and 'h' in 'thog' are also characters in 'https://'.
# This function strips only the exact to_strip string provided, and doesn't
# change the original string if it doesn't start with to_strip.
# So strict_lstrip('https://thog.com', 'https://') will return 'thog.com'
# and strict_lstrip('https:google', 'ht') will return 'tps:google'
def strict_lstrip(orig, to_strip):
    assert isinstance(orig, str), "non-string provided as orig to strict_lstrip: {}".format(orig)
    assert isinstance(to_strip, str), "non-string provided as to_strip to strict_lstrip: {}".format(to_strip)

    if not orig.startswith(to_strip):
        return orig

    new = orig[len(to_strip):]
    return new

# strict_rstrip is to rstrip as strict_lstrip is to lstrip
def strict_rstrip(orig, to_strip):
    assert isinstance(orig, str), "non-string provided as orig to strict_rstrip: {}".format(orig)
    assert isinstance(to_strip, str), "non-string provided as to_strip to strict_rstrip: {}".format(to_strip)

    if not orig.endswith(to_strip):
        return orig

    new = orig[:len(orig) - len(to_strip)]
    return new

if __name__ == "__main__":
    print(get_minecraft_path())
