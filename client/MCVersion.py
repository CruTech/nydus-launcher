
import subprocess
import os
import json
from nydus.common import validity
from nydus.client import utils

# Class for storing everything we need to launch
# a specific version of Minecraft

# The json at ~/.minecraft/versions/version_manifest_v2.json has info on all the
# different Minecraft versions available. Specifically, it gives where to
# download a json file for each version, and this json tells you the rest
# you need to know.

# Each of those version-specific json files is placed under
# ~/.minecraft/versions/<version>/<version>.json
# The version-specific jsons tell you many of the other things needed for that
# version to run, including a whole lot of other jar libraries that you should
# download and put under ~/.minecraft/libraries at the paths they individually
# specify.

# TODO
# There should also be a ~/.minecraft/versions/<version>/<version>.jar
# I don't know where you download that from.

# The json file which defines everything for this Minecraft version
# also has URLs and sha1 hashes for downloading each jar file if it doesn't
# exist.
# This class should download any such files that aren't already downloaded.

# OptiFine versions are different in a few ways.
# They do specify a few jars needed, but usually don't include
# download URLs and hashes; the file has to already exist, or else
# it won't work.
# OptiFine versions also usually inherit from the official Minecraft versions,
# so there needs to be a facility for detecting inheritance and doing
# everything in the ancestor version also.


class MCVersion:


    def __init__(self, version):

        if not validity.is_valid_minecraft_version(version):
            raise ValueError("Must provide valid Minecraft version to MCVersion constructor. Was given {}".format(version))

        self.version = version
        self.jars = []

    """
    Reads the json file defining this Minecraft version.
    Fills out the class with all the relevant data;
    jar files needed, class name to run when launching, so forth.
    Also processes ancestor versions if this one inherits from
    another by making more MCVersions instances.
    """
    def read_json_file(self):
        pass

    """
    Downloads the version-defining json file if it doesn't
    already exist.
    """
    def download_json_file(self):
        pass

    """
    Returns a boolean. True if the json file defining this Minecraft
    version exists; false if it doesn't.
    """
    def json_file_exists(self):
        return validity.is_valid_file(self.get_json_file())

    """
    Returns a string; the path to the file that tells us everything about
    this Minecraft version.
    """
    def get_json_file(self):
        pass

    """
    mc_account: an instance of MCAccount to provide the username,
        uuid, and acess token needed to launch.
    Launches an instance of Minecraft of the version
    stored in this class. Everything other than mc_account
    is provided by the version data and version-based json files.
    """
    def launch(self, mc_account):
        pass
