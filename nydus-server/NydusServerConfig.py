
import os

IPADDR = "IpAddr"
PORT = "Port"
CERTFILE = "CertFile"
CERTPRIVKEY = "CertPrivKey"
MCVERSION = "McVersion"
SERVER_PARNAMES = [IPADDR, PORT, CERTFILE, CERTPRIVKEY, MCVERSION]
SERVER_DEFCONFIG = {
    IPADDR: "192.168.1.1"
    PORT: "2011"
    CERTFILE: "nydus-server.crt"
    CERTPRIVKEY: "nydus-server.key"
    MCVERSION: "1.20.6"
}

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

        self.ip_addr = SERVER_DEFCONFIG[IPADDR]
        self.port = SERVER_DEFCONFIG[PORT]
        self.cert_file = SERVER_DEFCONFIG[CERTFILE]
        self.cert_privkey = SERVER_DEFCONFIG[CERTPRIVKEY]
        self.mc_version = SERVER_DEFCONFIG[MCVERSION]

        self.path = path
        self.read_config_file()

    """
    This function is expected to be given the remainder of a line
    from a config file, after the parameter name has been removed
    from the line.
    It returns the corresponding value if the line is formatted
    correctly, raises an exception if not.
    """
    def read_config_value(self, rest):
        rest = rest.strip()
        if rest.startswith("="):
            value = rest[1:]
            value = value.strip()
            return value
        else:
            raise ValueError("Could not find value on line {} of configuration file. Rest of line was '{}'".format(nline, rest))


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

                if line.startswith(IPADDR):
                    rest = line[len(pname):]
                    self.ip_addr = self.read_config_value(rest)
                elif line.startswith(PORT):
                    rest = line[len(pname):]
                    self.port = self.read_config_value(rest)
                elif line.startswith(CERTFILE):
                    rest = line[len(pname):]
                    self.cert_file = self.read_config_value(rest)
                elif line.startswith(CERTPRIVKEY):
                    rest = line[len(pname):]
                    self.cert_privkey = self.read_config_value(rest)
                elif line.startswith(MCVERSION):
                    rest = line[len(pname):]
                    self.mc_version = self.read_config_value(rest)
                else:
                    raise ValueError("Unknown parameter on line {} of configuration file. Line was '{}'".format(nline, line))

                nline += 1

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
