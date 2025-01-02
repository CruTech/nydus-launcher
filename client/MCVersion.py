
import subprocess
import os
import json
from nydus.common import validity
from nydus.client import utils
from nydus.common import MCAccount

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


# Sample launch:
# "java -cp {} -Xmx2G -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1NewSizePercent=20 -XX:G1ReservePercent=20 -XX:MaxGCPauseMillis=50 -XX:G1HeapRegionSize=32M -Dlog4j.configurationFile=/home/<username>/.minecraft/assets/log_configs/client-1.12.xml net.minecraft.client.main.Main --username {} --version 1.20.6 --gameDir /home/<username>/.minecraft --assetsDir /home/<username>/.minecraft/assets --assetIndex 16 --uuid {} --accessToken {} --clientId {} --xuid {} --userType msa --versionType release --quickPlayPath /home/<username>/.minecraft/quickPlay/java/1723272866743.json".format(cpjars, mc_username, mc_uuid, mc_access_tok, client_id, xuid)

# Important points
# -cp is the list of jarfiles needed. You get the list from the version JSON file,
# expand to absolute paths for each jar, and concatentate them all colon-separated.
# -cp is easy.

# -Dlog4j.configurationFile just make it whatever xml file is under .minecraft/assets/log_configs.

# net.minecraft.client.main.Main is the main class. It's found under the mainClass key in
# the version JSON file.

# --username, --version, --uuid, and --accessToken are all received from the Nydus Server.

# --gameDir is obvious; it'll always be the same.

# --assetsDir looks like it'll always be the same.

# --assetIndex we can probably just keep the same.

# --clientId's source is not known, but it is known that Minecraft will
# launch without it, so just don't include it.

# --xuid's value can be found in .minecraft/launcher_accounts.json.
# Under the "accounts" key there are alphanumeric keys which are seemingly
# recording the accounts which have logged in to the Minecraft launcher.
# Each of these has a "remoteId" key which is the value to give to xuid.
# However this requires someone to have already logged in as that user to
# the Minecraft launcher, which won't be the case in our situation.
# And we know experimentally Minecraft will launch without --xuid, so
# just don't include it.

# --userType looks like something we can just leave.

# --versionType is probably fine. Might want to check that OptiFine
# uses the same, but other than that there's probably nothing to do there.

# --quickPlayPath can probably be ommitted; the path given to it isn't
# even there on the filesystem. And I assume it's something to do with getting
# the launcher to open a preferred Minecraft instance quickly. Since the Nydus
# launcher specifies the desired Minecraft instance and opens it directly,
# that's irrelevant to our situation.


# Conclusion:
# For a successful Minecraft launch, we want
# -cp: jars optained from version JSON
# -Dlog4j.configurationFile: whatever xml is under .minecraft/assets/log_configs
# mainClass from version JSON
# --username, --version, --uuid, --accessToken from server
# --gameDir: /home/<username>/.minecraft
# --assetsDir: /home/<username>/.minecraft/assets
# --assetIndex: 16
# --userType: msa
# --versionType: release


class MCVersion:


    def __init__(self, version, mc_account):

        if not validity.is_valid_minecraft_version(version):
            raise ValueError("Must provide valid Minecraft version to MCVersion constructor. Was given {}".format(version))

        if not isinstance(mc_account, MCAccount):
            raise TypeError("Must provide an MCAccount to MCVersion constructor. Was given a {}".format(type(mc_account)))

        self.version = version

        # To be filled in from reading the version's JSON file
        self.jars = []
        self.main_class = ""

        # MCAccount contains username, uuid, access token
        # Data obtained from server.
        self.mc_account = mc_account

        # Standard patterns based on who is logged in
        self.game_dir = utils.get_minecraft_path()
        self.assets_dir = utils.get_minecraft_assets_path()

        # Computed by looking under the assets dir
        self.log_config = ""

        # Hard coded, observed from past Minecraft launches
        self.asset_index = 16
        self.user_type = "msa"
        self.version_type = "release"

        self.find_log_config()
        self.read_json_file()

    """
    Looks for the directory log_configs under the minecraft assets
    directory. If it exists and contains an xml file, the path
    to that file is the log config parameter's value.
    This function finds that xml file and saves the path
    in the relevant class attribute.
    If there are multiple xml files, the first one found will be used.
    Raises an Exception if such a file can't be found.
    """
    def find_log_config(self):
        log_cdir = os.path.join(self.assets_dir, "log_configs")
        if not os.path.isdir(log_cdir):
            raise OSError("No directory at {} to get Log4J config.".format(log_cdir))

        contents = os.listdir(log_cdir)
        for name in contents:
            if name.endswith(".xml") and os.path.isfile(name):
                self.log_config = os.path.join(log_cdir, name)
                return

        raise OSError("No xml file in {} to get Log4J config from.".format(log_cdir))

    """
    Reads the json file defining this Minecraft version.
    Fills out the class with all the relevant data;
    jar files needed and class name to run when launching.
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
    Launches an instance of Minecraft of the version
    stored in this class.
    """
    def launch(self):
        pass
