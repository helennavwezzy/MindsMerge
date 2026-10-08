import logging
import time
from contextlib import contextmanager
from typing import cast

from .formatter import CustomFormatter


class CustomLogger(logging.Logger):
    @contextmanager
    def log_timespan(self, enter_msg: str, exit_fmt: str = "Completed in %sms"):
        self.info(enter_msg)
        _begin = time.time()
        try:
            yield
        finally:
            _end = time.time()
            self.info(exit_fmt, round(1000 * (_end - _begin)))


_stream_handler = logging.StreamHandler()
_stream_handler.setFormatter(CustomFormatter())

logging.setLoggerClass(CustomLogger)
logging.basicConfig(level=logging.ERROR)


def getLogger(name: str, level: int = logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(_stream_handler)
    return cast(CustomLogger, logger)
