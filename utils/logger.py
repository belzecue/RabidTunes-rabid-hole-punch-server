"""
Logger utilities
This file provides some helping config to have a nice logging
mechanism that is easy to use in other parts of the code
By default logs printed with this _logger will be output to console
and a rotating log file
"""

import logging
from logging import Logger
from logging.handlers import RotatingFileHandler

LOG_FILE_NAME = "rabid-hole-punch.log"
LOG_MAX_BYTES = 10000000  # 10 MB
LOG_BACKUP_COUNT = 10
LOG_LEVEL = logging.INFO


def get_logger(logger_name: str) -> Logger:
    logger = logging.getLogger(logger_name)
    logger.setLevel(LOG_LEVEL)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    ch = logging.StreamHandler()
    ch.setLevel(LOG_LEVEL)
    ch.setFormatter(formatter)
    # ch.emit = _colored_emit(ch.emit) This line colors the output but also puts weird chars on file log output
    logger.addHandler(ch)

    rf = RotatingFileHandler(LOG_FILE_NAME, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT)
    rf.setLevel(LOG_LEVEL)
    rf.setFormatter(formatter)
    logger.addHandler(rf)

    return logger


def _colored_emit(fn):
    def new(*args):
        levelno = args[0].levelno
        if levelno >= logging.CRITICAL:
            color = '\x1b[31;1m'
        elif levelno >= logging.ERROR:
            color = '\x1b[31;1m'
        elif levelno >= logging.WARNING:
            color = '\x1b[33;1m'
        elif levelno >= logging.INFO:
            color = '\x1b[34;1m'
        elif levelno >= logging.DEBUG:
            color = '\x1b[35;1m'
        else:
            color = '\x1b[0m'
        args[0].msg = "{0}{1}\x1b[0m".format(color, args[0].msg)
        return fn(*args)
    return new
