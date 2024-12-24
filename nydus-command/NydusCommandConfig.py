
import os
import validity

IPADDR = "IpAddr"
PORT = "Port"
CERTFILE = "CertFile"
CERTPRIVKEY = "CertPrivKey"
MCVERSION = "McVersion"
MSALCID = "MSALClientID"
ALLOCFILE = "AllocFile"
COMMAND_PARNAMES = [IPADDR, PORT, CERTFILE, CERTPRIVKEY, MCVERSION]
COMMAND_DEFCONFIG = {
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
# In the case of the Nydus Command module, there may be
# configuration items present in the configuration file
# which the Command does not need to store. Only data which
# needs to be stored appears in the VARNAMES dictionary.
COMMAND_VARNAMES = {
    ALLOCFILE: "alloc_file",
}

class NydusCommandConfig:

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

        for parname in COMMAND_PARNAMES:
            if parname in COMMAND_VARNAMES:
                setattr(self, COMMAND_VARNAMES[parname], COMMAND_DEFCONFIG[parname])

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
                for pname in COMMAND_PARNAMES:

                    # Only keep studying the file if the parameter
                    # name is one the Nydus Command needs to store.
                    if not pname in COMMAND_VARNAMES:
                        continue

                    if line.startswith(pname):
                        rest = line[len(pname):]
                        rest = rest.strip()
                        if rest.startswith("="):
                            value = rest[1:]
                            value = value.strip()
                            setattr(self, COMMAND_VARNAMES[pname], value)
                            found_param = True
                            break
                        else:
                            raise ValueError("Could not find value on line {} of configuration file. Parameter name {} appeared with no equals sign. Rest of line was '{}'".format(nline, pname, rest))

                if not found_param:
                    raise ValueError("Unknown parameter on line {} of configuration file. Line was '{}'".format(nline, line))

                nline += 1

    def validate_config(self):
        if not validity.is_valid_file(self.alloc_file):
            raise ValueError("Value for {} is not a file, cannot be found, or cannot be read: {}".format(ALLOCFILE, self.alloc_file))

    def get_alloc_file(self):
        return self.alloc_file
