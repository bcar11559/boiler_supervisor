from applibs.logger import ApplicationLogger
ApplicationLogger()
logger = ApplicationLogger.logger

from micropython import const

import time, machine

from applibs.comms import initialise_wifi, connect_wifi, wifi_connected, wan_ok
from applibs.timing import set_clock
from applibs.sysutils import get_platform
from applibs.mainloop import maintest_rgb_blink

VERSION = const("dev0.0.2")
 
logger.info(f'Firmware version: {VERSION}')

is_micropython = get_platform()

wlan = initialise_wifi()
connect_wifi(wlan)

if wifi_connected(wlan):
    if wan_ok():
        set_clock()

try:
    logger.info(f'Entering main loop now...')

    while True:
        maintest_rgb_blink()

except Exception as e:
    logger.exception("Exception raised when running mainloop.")

finally:
    for i in range(-5):
        logger.info(f'Dropped out of main loop somehow, hard reset in {-i}s')
        time.sleep(1)
    machine.reset()
        
