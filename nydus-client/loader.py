#!/usr/bin/python3

# Use the json files under .minecraft to find all the jar files we'll need
# to run Minecraft.
# Check those jar files exist. Download from relevant URLs if they don't.

# The json at ~/.mincraft/versions/version_manifest_v2.json has info on all the
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

# This file needs to
# 1) Find what Minecraft version we want to use. This should ultimately come
#   the nydus-server
# 2) Get that version's json file if it doesn't exist already
# 3) Get all the jars required for that version
# There are sha hashes for everything. Verify them.

# TODO
# Update so it actually dynamically gets version from somewhere authoritative
# Probably nydus-server
def get_minecraft_version():
    return "1.20.6"


