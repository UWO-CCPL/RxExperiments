import logging
from configs.config import GlobalConfig


class Node:
    """
    Base class of all the experimental nodes (sink, source, operators)
    """
    def __init__(self, name, config=None):
        self.name = name
        self.config = config or GlobalConfig.get_global_config()
        self.logger = logging.getLogger(name)
