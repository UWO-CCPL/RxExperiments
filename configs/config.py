import configparser
import json
import os


class GlobalConfig:
    _config: dict = None

    @classmethod
    def initialize_global_configuration(cls, config_file=None):
        config_file = config_file or os.path.join(os.path.dirname(__file__), "defaults.json")
        with open(config_file, "r") as f:
            config = json.load(f)
        cls._config = config

    @classmethod
    def get_global_config(cls):
        if cls._config is None:
            raise ValueError("Config is not initialized. Call initialize_global_configuration first")

        return cls._config
