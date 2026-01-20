import logging
from logging.handlers import RotatingFileHandler

log_format = "%(asctime)-15s :%(name)-25s :%(levelname)-9s :%(message)s"
logging.basicConfig(level=logging.DEBUG)

formatter = logging.Formatter(log_format, datefmt="%b-%d %H:%M:%S",)
root_logger = logging.getLogger()
root_handler = root_logger.handlers[0]
root_handler.setFormatter(formatter)

file_handler = RotatingFileHandler(
    "main.log",
    mode='a', 
    maxBytes=1*1024*1024, 
    backupCount=2)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
root_logger.addHandler(file_handler)

logger = logging.getLogger(__name__)

import platform

def is_micropython():
    platform_info = platform.platform()
    if platform_info.startswith("Micropython"):
        logger.info(f'Running Micropython: {platform_info}')
        return True
    else:
        logger.info(f'Running CPython: {platform_info} ')
        return False
