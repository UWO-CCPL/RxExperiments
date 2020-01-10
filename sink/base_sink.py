import logging

from rx.core import Observer

from datamodel.node import Node


class BaseSink(Node, Observer):
    def __init__(self, name, on_next=None, on_error=None, on_completed=None):
        on_error = on_error or self._error_handler
        Node.__init__(self, name)
        Observer.__init__(self, on_next=on_next, on_error=on_error, on_completed=on_completed)

    def _error_handler(self, err: Exception):
        logging.error(err)
