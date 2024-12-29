
import os
from nydus.common import validity
from nydus.common import Config

SERVERIPADDR = "ServerIpAddr"
PORT = "Port"
CACHAINFILE = "CaChainFile"
CLIENT_PARNAMES = [SERVERIPADDR, PORT, CACHAINFILE]
CLIENT_DEFCONFIG = {
    SERVERIPADDR: "192.168.1.1",
    PORT: "2011",
    CACHAINFILE: "nydus-ca.crt",
}

# Maps between the parameter named used in the config file
# and the attribute name used in the Config class
CLIENT_VARNAMES = {
    SERVERIPADDR: "server_ip",
    PORT: "port",
    CACHAINFILE: "ca_chain",
}

class ClientConfig(Config):

    """
    path: a string, path to the configuration file to read
    """
    def __init__(self, path):
        assert isinstance(path, str), "Configuration file path must be a string. Was {}".format(path)

        if not os.path.isfile(path):
            raise FileNotFoundError("Configuration file could not be found: {}".format(path))

        for parname in CLIENT_PARNAMES:
            setattr(self, CLIENT_VARNAMES[parname], CLIENT_DEFCONFIG[parname])

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
                for pname in CLIENT_PARNAMES:
                    if line.startswith(pname):
                        rest = line[len(pname):]
                        rest = rest.strip()
                        if rest.startswith("="):
                            value = rest[1:]
                            value = value.strip()
                            setattr(self, CLIENT_VARNAMES[pname], value)
                            found_param = True
                            break
                        else:
                            raise ValueError("Could not find value on line {} of configuration file. Parameter name {} appeared with no equals sign. Rest of line was '{}'".format(nline, pname, rest))

                if not found_param:
                    raise ValueError("Unknown parameter on line {} of configuration file. Line was '{}'".format(nline, line))

                nline += 1

        
    def validate_config(self):
        if not validity.is_valid_ipaddr(self.server_ip):
            raise ValueError("Value for {} is not a valid IP address: {}".format(SERVERIPADDR, self.server_ip))

        if not validity.is_valid_port(self.port):
            raise ValueError("Value for {} is not a valid port: {}".format(PORT, self.port))

        if not validity.is_valid_file(self.ca_chain):
            raise ValueError("Value for {} is not a file, cannot be found, or cannot be read: {}".format(CACHAINFILE, self.ca_chain))

        def get_server_ip(self):
            return self.server_ip

        def get_port(self):
            return self.port

        def get_ca_chain(self):
            return self.ca_chain
