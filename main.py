import logging
logger = logging.getLogger(__name__)

from initialise import is_micropython


if is_micropython():
    import machine
else:
    import os

from control import mainloop

VERSION = "dev0.0.1"
DEBUG = False
logger.info(f'Firmware version: {VERSION}')
logger.info(f'Logging Level: {logger.level}')

try:
    logger.info(f'Entering main loop now...')
    mainloop.main()
except Exception as e:
    logger.exception("Exception raised when running mainloop.")
finally:
    if is_micropython():
        logger.info(f'Rebooting now...')
        machine.reset()
    else:
        os.sys.exit()
        

