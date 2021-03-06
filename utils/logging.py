import logging
import os

from configs.config import GlobalConfig
import colorlog
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


def configure_logger_to_output(logger: logging.Logger = logging.root, output=None, level=logging.INFO):
    output = output or widgets.Output()
    handler = NotebookOutputHandler(output)
    handler.setFormatter(colorlog.ColoredFormatter(
        "%(asctime)s %(log_color)s%(levelname)-6s%(reset)s %(name)s: %(blue)s%(message)s\n",
        reset=True,
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    ))
    logger.addHandler(handler)

    config = GlobalConfig.get_global_config()
    handler = logging.FileHandler(os.path.join(config["data"]["base"], "events.log"))
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)-6s %(name)s: %(message)s\n", datefmt="%Y-%m-%d %H:%M:%S"))
    logger.addHandler(handler)

    logger.setLevel(level)
    return output
