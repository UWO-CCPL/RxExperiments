import logging
import queue
from logging.handlers import QueueHandler, QueueListener
from typing import Optional, IO

import ipywidgets as widgets


class NotebookOutputHandler(logging.StreamHandler):

    def __init__(self, output: widgets.Output) -> None:
        super().__init__()
        self.output = output

    def emit(self, record: logging.LogRecord) -> None:
        if self.filter(record):
            msg = self.format(record)
            if record.levelno > logging.WARNING:
                self.output.append_stderr(msg)
            else:
                self.output.append_stdout(msg)


def configure_logger_to_output(logger: logging.Logger, output=None):
    output = output or widgets.Output()
    handler = NotebookOutputHandler(output)
    logger.addHandler(handler)
    return output
