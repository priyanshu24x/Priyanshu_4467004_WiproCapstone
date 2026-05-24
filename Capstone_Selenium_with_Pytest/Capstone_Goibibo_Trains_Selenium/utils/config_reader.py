# Reads the config.properties file and gives values to other parts of the framework.

import os

class ConfigReader:
    _config = {}

    @classmethod
    def load_config(cls):
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "config", "config.properties"
        )
        with open(config_path) as configfile:
            for line in configfile:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    cls._config[key.strip()] = value.strip()
        return cls._config

    @classmethod
    def get(cls, key):
        return cls.load_config().get(key)

