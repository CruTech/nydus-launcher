
import os
from nydus.common import validity
from nydus.common import Config

IPADDR = "IpAddr"
PORT = "Port"
CERTFILE = "CertFile"
CERTPRIVKEY = "CertPrivKey"
MCVERSION = "McVersion"
MSALCID = "MSALClientID"
ALLOCFILE = "AllocFile"
SERVER_PARNAMES = [IPADDR, PORT, CERTFILE, CERTPRIVKEY, MCVERSION]
SERVER_DEFCONFIG = {
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
SERVER_VARNAMES = {
    IPADDR: "ip_addr",
    PORT: "port",
    CERTFILE: "cert_file",
    CERT_PRIVKEY: "cert_privkey",
    MCVERSION: "mc_version",
    MSALCID: "msal_cid",
    ALLOCFILE: "alloc_file",
}

class ServerConfig(Config):

    def validate_config(self):
        if not validity.is_valid_ipaddr(self.ip_addr):
            raise ValueError("Value for {} is not a valid IP address: {}".format(IPADDR, self.ip_addr))

        if not validity.is_valid_port(self.port):
            raise ValueError("Value for {} is not a valid port: {}".format(PORT, self.port))

        if not validity.is_valid_file(self.cert_file):
            raise ValueError("Value for {} is not a file, cannot be found, or cannot be read: {}".format(CERTFILE, self.cert_file))

        if not validity.is_valid_file(self.cert_privkey):
            raise ValueError("Value for {} is not a file, cannot be found, or cannot be read: {}".format(CERTPRIVKEY, self.cert_privkey))

        if not validity.is_valid_minecraft_version(self.mc_version):
            raise ValueError("Value for {} is not a valid Minecraft version: {}".format(MCVERSION, self.mc_version))

        if not validity.is_valid_msal_cid(self.msal_cid):
            raise ValueError("Value for {} is not a valid MSAL Client ID: {}".format(MSALCID, self.msal_cid))

        if not validity.is_valid_file(self.alloc_file):
            raise ValueError("Value for {} is not a file, cannot be found, or cannot be read: {}".format(ALLOCFILE, self.alloc_file))

    def get_ip_addr(self):
        return self.ip_addr

    def get_port(self):
        return self.port

    def get_cert_file(self):
        return self.cert_file

    def get_cert_privkey(self):
        return self.cert_privkey

    def get_mc_version(self):
        return self.mc_version

    def get_msal_cid(self):
        return self.msal_cid

    def get_alloc_file(self):
        return self.alloc_file