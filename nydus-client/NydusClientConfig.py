
import os

SERVERIPADDR = "ServerIpAddr"
PORT = "Port"
CACHAINFILE = "CaChainFile"
CLIENT_PARNAMES = [SERVERIPADDR, PORT, CACHAINFILE]
CLIENT_DEFCONFIG = {
    SERVERIPADDR: "192.168.1.1"
    PORT: "2011"
    CACHAINFILE: "nydus-ca.crt"
}

class NydusClientConfig:

    """
    path: a string, path to the configuration file to read
    """
    def __init__(self, path):
        assert isinstance(path, str), "Configuration file path must be a string. Was {}".format(path)

        if not os.path.isfile(path):
            raise FileNotFoundError("Configuration file could not be found: {}".format(path))

        self.server_ip = CLIENT_DEFCONFIG[SERVERIPADDR]
        self.port = CLIENT_DEFCONFIG[PORT]
        self.ca_chain = CLIENT_DEFCONFIG[CACHAINFILE]

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

                if line.startswith(SERVERIP):
                    rest = line[len(SERVERIP
                found_param = False
                for pname in CLIENT_PARNAMES:
                    if line.startswith(pname):
                        found_param = True

                        rest = line[len(pname):]
                        rest = rest.strip()
                        if rest.startswith("="):
                            value = rest[1:]
                            value = value.strip()
                            self.config_params[pname] = value
                            break
                        else:
                            raise ValueError("Could not find value on line {} of configuration file. Parameter name {} appeared with no equals sign. Rest of line was '{}'".format(nline, pname, rest))

                if not found_param:
                    raise ValueError("Unknown parameter on line {} of configuration file. Line was '{}'".format(nline, line))

                nline += 1

        
        def get_server_ip(self):
            return self.server_ip

        def get_port(self):
            return self.port

        def get_ca_chain(self):
            return self.ca_chain