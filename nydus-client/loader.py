#!/usr/bin/python3

import common
import os
import json
from json.decoder import JSONDecodeError
from DownloadFile import DownloadFile

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

# JSON structure tags
VERSIONS_BLOCK = "version"
VERSION_ID = "id"
SHA1_HASH = "sha1"
DOWNLOAD_URL = "url"
LIBRARY_KEY = "libraries"
SUBPATH = "path"


# TODO
# Update so it actually dynamically gets version from somewhere authoritative
# Probably nydus-server
def get_minecraft_version():
    return "1.20.6"

"""
Given path to a file, reads the file and returns 
json data accessible via list/dictionary style interface,
as produced by json.load
"""
def read_json_file(filepath):
    assert isinstance(filepath, str), "Filepath should have been a string. Was {}".format(filepath)

    assert os.path.isfile(filepath), "Filepath did not exist: {}".format(filepath)

    with open(filepath, "r") as f:

        try:
            data = json.load(f)
        except JsonDecodeError as e:
            raise ValueError("Failed to parse json in {} at line {} col {} char {}"\
                    .format(filepath, e.lineno, e.colno, e.pos))
    return data

"""
Given a json data object (using the list/dictionary style
interface returned by json.load) returns the data at
a specified position.
jstruct: the json data object. This needs to be a dictionary, not a list
key: if this key exists at the top level of the json data, return
    the data under the key.
raise: if the key is not found and the raise parameter is True,
    raise an exception. If the key is not found and raise is
    False, return None.
    'raise' being False does not guarantee no exception will be
    raised by this function; it may raise an exception if the
    provided arguments are the wrong data types.
"""
def get_json_key(jstruct, key, raise=True):

    assert isinstance(jstruct, dict), "JSON structure given to get_json_key must be a dict. It was a {}"\
            .format(type(jstruct))

    assert isinstance(key, str), "key given to get_json_key must be a string. It was {}".format(key)

    if key in jstruct:
        return jstruct[key]

    if raise:
        raise KeyError("key {} not in given Json structure".format(key))

    return None

"""
Given a json data object (the list/dictionary representation
of the kind returned by json.load) looks through a list and
returns the first element in the list which contains a specified
key and value pair. Returns only the first such element.
jlist: the json data object. Needs to be a list.
keyattr: search through the list until an element which has this key is found
valattr: if the element has 'valattr' as the value corresponding to key 'keyattr',
    then it is returned.
raise: if no element with the right key/value pair is found and 'raise' is True,
    raise an exception. If it's false, return None.
    'raise' being False does not guarantee no exception will be
    raised by this function; it may raise an exception if the
    provided arguments are the wrong data types.
"""
def get_from_json_list(jlist, keyattr, valattr, raise=True):
    assert isinstance(jlist, list), "JSON structure given to get_from_json_list must be a list. It was a {}"\
            .format(type(jlist))

    assert isinstance(keyattr, str), "key given to get_from_json_list must be a string. It was {}"\
            .format(keyattr)

    assert isinstance(valattr, str), "value given to get_from_json_list must be a string. It was {}"\
            .format(valattr)
    
    for elem in jlist:
        if isinstance(elem, dict):
            if keyattr in elem:
                if valattr == elem[keyattr]:
                    return elem

    if raise:
        raise AttributeError("No element with key {} and value {} in given JSON structure".\
                format(keyattr, valattr))

    return None

"""
Gets all the available Minecraft versions that we know about
"""
def get_all_versions():
    mc_path = common.get_minecraft_path()

    jdata = read_json_file(get_manifest_path())

    version_json = get_json_key(jdata, VERSIONS_BLOCK)

    all_versions = []
    for vers in version_json:
        all_versions.append(vers[VERSION_ID])
    return all_versions

def is_valid_version(version):
    versions = get_all_versions()
    if version in versions:
        return True
    return False

"""
Returns the path (including filename) to the json which
describes all the libraries needed for the given Minecraft
version
"""
def get_version_json_path(version):
    
    if not is_valid_version(version):
        raise ValueError("version was not valid: {}".format(version))
    mc_path = common.get_minecraft_path()
    
    version_json = os.path.join(mc_path, "versions", version, "{}.json".format(version))
    return version_json

"""
Gives full path to the version manifest file
"""
def get_manifest_path():
    mc_path = common.get_minecraft_path()
    manifest_path = os.path.join(mc_path, "versions", "version_manifest_v2.json")

"""
Given the desired minecraft version, extracts that version's
json dictionary from the version manifest file.
This data is expected to include 'id', 'sha1', and 'url'
which can be used for downloading
"""
def get_version_manifest_data(version):
    if not is_valid_version(version):
        raise ValueError("version was not valid: {}".format(version))

    # TODO check file exists
    with open(get_manifest_path(), "r") as f:

        # TODO check json data valid
        jdata = json.load(f)

    # check json has the right entries
    version_json = jdata[VERSIONS_BLOCK]

    for block in version_json:
        if VERSION_ID in block:
            if block[VERSION_ID] == version:
                return block
    raise ValueError("Could not find data block for version {} in manifest {}".format(version, manifest_path))

"""
Using the DownloadFile class and extracting data from
the version manifest file, ensures the requested version's
json file is either already in the right place or downloads
it.
"""
def download_version_json(version):
    if not is_valid_version(version):
        raise ValueError("version was not valid: {}".format(version))

    version_data = get_version_manifest_data(version)
    fpath = get_version_json_path(version)
    fname = os.path.basename(fpath)
    dirpath = os.path.dirname(fpath)

    sha1 = version_data[SHA1_HASH]
    url = version_data[DOWNLOAD_URL]

    vj_download = DownloadFile(url, sha1, name=fname, path=dirpath)
    vj_download.download()

"""
Goes through all the libraries files in the requested version's
json file and downloads them all
"""
def download_libraries(version):
    if not is_valid_version(version):
        raise ValueError("version was not valid: {}".format(version))

    vj_path = get_version_json_path(version)
    with open(vj_path, "r") as f:
        # TODO check json data valid
        jdata = json.load(f)

    # TODO check json has the right entries
    libraries = jdata[LIBRARY_KEY]

    # split into more functions
    for obj_dict in libraries:


        # If there are rules applying to this object,
        # only download if it is for linux
        # But if there are no rules, download it anyway

        do_download = False
        if RULES_KEY in obj_dict:
            rule_data = obj_dict["rules"]

            for rule in rules_data:
                if rule["action"] == "allow":
                    if rule["os"]["name"] == "linux":
                        do_download = True
        else:
            do_download = True

        if do_download:
            download_data = obj_dict["downloads"]["artifact"]
            url = download_data[DOWNLOAD_URL]
            sha1 = download_data[SHA1_HASH]
            path = download_data[SUBPATH]
            
            # The path for these artifacts doesn't include the dir
            # 'libraries' that they are all under
            mc_path = common.get_minecraft_path()
            full_path = os.path.join(mc_path, "libraries", path)
            fname = os.path.basename(full_path)
            dirpath = os.path.basename(fullpath)

            lib_download = DownloadFile(url, sha1, name=fname, path=dirpath)
            lib_download.download()
        
    
