#!/usr/bin/python3

import common
import os
import requests

"""
Class theory

This class will include all the info needed to actually download a file used in Minecraft
This includes
  * The position on the filesystem where it should go
  * The expected sha1 hash of the file
  * The url at which the file will be found

The class will also have the utilities needed to download the file.
When file download is requested, we need to
    1) Check if the file already exists
    2) If it exists, check if it has the right sha1 hash. If so, we're done -> Success
    3) If it has the wrong hash or doesn't exist, check if the path to the file's location exists
    4) If the path doesn't exist, make it
    5) Download the file from the interwebs and place it in the right spot.
    6) Check the newly downloaded file has the right hash. If so, we're done -> Success

Possible (unrecoverable) error cases:
    * existing file is missing/wrong hash and
        - path to file's location can't be created
        - url doesn't exist
        - connection gets interrupted
        - location to write the file is unwritable
        - file downloads fine but has the wrong hash

Is there any reason to delay downloading the file?
Should the class download the file as soon as it is instantiated?
"""

MC_MODE=0o775

class DownloadFile:

    # url must be correct according to common.is_download_url
    # path, if given, must be absolute
    # path need not exist
    # path INCLUDES the final filename
    """
    name: a string representing the file
    """
    def __init__(self, name, url, sha1, path=""):
        self.name = name

        self.url = url

        assert common.is_download_url(url), "url provided to DownloadFile is not a valid file downloading url: {}".format(url)

        # TODO validate sha1 is a real hash
        self.sha1 = sha1

        self.path = path

        if self.path == "":
            self.construct_path()

    # Only if the path at which the file should be stored is unknown,
    # infer it using filename and download URL
    def construct_path(self):
        if self.path != "":
            return
        
        upath = common.get_url_path(self.url)
        mcpath = common.get_minecraft_path()

        if upath.startswith("/"):
            upath = upath.lstrip("/")

        self.path = "{}/{}".format(mcpath, upath)

    
