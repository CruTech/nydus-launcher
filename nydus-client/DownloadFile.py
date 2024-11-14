#!/usr/bin/python3

import common
import os

MC_MODE=0o775

class DownloadFile:

    # url must be correct according to common.is_download_url
    # path, if given, must be absolute
    # path need not exist
    # path INCLUDES the final filename
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

    # Create the needed directories to store the file in
    # But only if they don't exist
    def create_path(self):
        # self.path includes final filename; we need
        # the path without the file to create intermediate directories
        
        # TODO
        # does makedirs have some return code or exception raise
        # that should be handled here?
        # it can raise FileExistsError, but we check that
        # before running it anyway
        dirpath = os.path.dirname(self.path)
        if not os.path.isdir(dirpath):
            # Make sure to create the new directories with the right
            # permissions, but set the umask back when we're done
            old_umask = os.umask(MC_MODE)
            os.makedirs(dirpath, MC_MODE)
            os.umask(old_umask)
