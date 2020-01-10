from rx.core import Observable, Observer
from rx.disposable import Disposable

from datamodel.node import Node


class BaseControl(Node, Observable, Observer):

    def __init__(self, name, config=None):
        Node.__init__(self, name, config)
        Observable.__init__(self, self.on_subscribe)
        Observer.__init__(self, self.on_command, self._error_handle)

    def on_command(self, x):
        """
        Called when observer.on_next called. The destination should be notified to update.
        :param x:
        :return:
        """
        pass

    def _error_handle(self, ex: Exception):
        self.logger.error("control error", exc_info=ex)

    def on_subscribe(self, observer, scheduler=None):
        """
        Override this function to retrieve control output data from the target.
        :param observer:
        :param scheduler:
        :return:
        """
        return Disposable()
