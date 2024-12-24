
import os
import validity

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

# TODO: check validity of form of each configuration item
class NydusServerConfig:

    """
    path: a string, path to the configuration file to read
    config_dict: a dictionary with string keys and values
        Each key is one configuration parameter.
        Each value is the default for that parameter.
    """
    def __init__(self, path):
        assert isinstance(path, str), "Configuration file path must be a string. Was {}".format(path)

        if not os.path.isfile(path):
            raise FileNotFoundError("Configuration file could not be found: {}".format(path))

        for parname in SERVER_PARNAMES:
            setattr(self, SERVER_VARNAMES[parname], SERVER_DEFCONFIG[parname])

        self.path = path
        self.read_config_file()
        self.validate_config()


    def read_config_file(self):

        # There may be exceptions trying to open the file
        # such as permission denied, or if it's been moved
        # since we checked for it (unlikely).
        # I don't want to except Exception but it would
        # be good to give more useful error messages than
        # python's defaults.
        with open(self.path, "r") as f:
            nline = 1
            for line in f:
                line = line.strip()

                # Empty line or comment
                if line == "" or line.startswith("#"):
                    continue
                
                # Look for the parameter name

                found_param = False
                for pname in SERVER_PARNAMES:
                    if line.startswith(pname):
                        rest = line[len(pname):]
                        rest = rest.strip()
                        if rest.startswith("="):
                            value = rest[1:]
                            value = value.strip()
                            setattr(self, SERVER_VARNAMES[pname], value)
                            found_param = True
                            break
                        else:
                            raise ValueError("Could not find value on line {} of configuration file. Parameter name {} appeared with no equals sign. Rest of line was '{}'".format(nline, pname, rest))

                if not found_param:
                    raise ValueError("Unknown parameter on line {} of configuration file. Line was '{}'".format(nline, line))

                nline += 1

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
