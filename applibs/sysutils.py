from applibs.logger import ApplicationLogger
logger = ApplicationLogger.logger

import platform

def get_platform():
    platform_info = platform.platform()
    if platform_info.startswith("MicroPython"):
        logger.debug(f'Running MicroPython: {platform_info}')
        return True
    else:
        logger.debug(f'Running CPython: {platform_info} ')
        return False