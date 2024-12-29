
import os
from nydus.common import validity
from nydus.common import Config

# Remember this needs to be the same as the server config file
CLI_CONFIG_FILE = "/etc/nydus-launcher/server.conf"

IPADDR = "IpAddr"
PORT = "Port"
CERTFILE = "CertFile"
CERTPRIVKEY = "CertPrivKey"
MCVERSION = "McVersion"
MSALCID = "MSALClientID"
ALLOCFILE = "AllocFile"
CLI_PARNAMES = [IPADDR, PORT, CERTFILE, CERTPRIVKEY, MCVERSION]
CLI_DEFCONFIG = {
    IPADDR: "192.168.1.1",
    PORT: "2011",
    CERTFILE: "nydus-server.crt",
    CERTPRIVKEY: "nydus-server.key",
    MCVERSION: "1.20.6",
    MSALCID: "1ab23456-7890-1c2d-e3fg-45h6789ijk01",
    ALLOCFILE: "nydus-alloc.csv"
}

# Maps between the parameter name used in the config file
# and the attribute name used in the Config class
# In the case of Nydus Cli, there may be
# configuration items present in the configuration file
# which the Cli does not need to store. Only data which
# needs to be stored appears in the VARNAMES dictionary.
CLI_VARNAMES = {
    ALLOCFILE: "alloc_file",
}

class CliConfig(Config):

    def __init__(self, path=CLI_CONFIG_FILE, parnames=CLI_PARNAMES, defconfig=CLI_DEFCONFIG, varnames=CLI_VARNAMES):
        super().__init(path, parnames, defconfig, varnames)

    def validate_config(self):
        if not validity.is_valid_file(self.alloc_file):
            raise ValueError("Value for {} is not a file, cannot be found, or cannot be read: {}".format(ALLOCFILE, self.alloc_file))

    def get_alloc_file(self):
        return self.alloc_file
