
import os

class NydusConfig:

    """
    path: a string, path to the configuration file to read
    config_dict: a dictionary with string keys and values
        Each key is one configuration parameter.
        Each value is the default for that parameter.
    """
    def __init__(self, path, config_dict={}):
        assert isinstance(path, str), "Configuration file path must be a string. Was {}".format(path)

        if not os.path.isfile(path):
            raise FileNotFoundError("Configuration file could not be found: {}".format(path))

        self.path = path
        self.config_params = config_dict

        self.validate_config_defaults()
        self.read_config_file()

    def validate_config_defaults(self):

        assert isinstance(self.config_params, dict), \
                "Parameter collection must be a dictionary. Was {}".format(self.config_params)

        for key in self.config_params:
            value = self.config_params[key]

            assert isinstance(key, str), \
                    "Parameter names must be strings. Found a parameter of type {}".format(type(key))

            assert isinstance(value, str), \
                    "Parameter default values must be strings. Found a parameter of type {}".format(type(value))


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
                for pname in self.config_params:
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

        """
        pname: string. Name of configuration parameter for which we'd like to get the value.
        """
        def get_config_value(self, pname):
            assert isinstance(pname, str), "Configuration parameter name must be a string. Was given {}".format(pname)

            if pname in self.config_params:
                return self.config_params[pname]
            
            raise KeyError("There is no configuration parameter named '{}'".format(pname))
