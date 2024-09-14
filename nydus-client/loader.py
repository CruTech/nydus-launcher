#!/usr/bin/python3

# Use the json files under .minecraft to find all the jar files we'll need
# to run Minecraft.
# Check those jar files exist. Download from relevant URLs if they don't.

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
    
if __name__ == "__main__":
    print(get_minecraft_path())
