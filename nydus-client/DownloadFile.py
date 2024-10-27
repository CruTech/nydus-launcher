#!/usr/bin/python3

import common

class DownloadFile:

    # url must be correct according to common.is_download_url
    # path, if given, must be absolute
    # path need not exist
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
