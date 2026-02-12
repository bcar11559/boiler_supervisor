from applibs.logger import ApplicationLogger
logger = ApplicationLogger.logger

import time
import ntptime
from machine import RTC
from micropython import const

#_ISO_FORMAT_STRING = const("{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}.{:03d}Z")

rtc = RTC()

def set_clock(ntpserver='svl1.ntp.se', ntptimeout=3):
    '''
    Set the board RTC with the NTP time.
    '''
    ntptime.host = ntpserver
    ntptime.timeout = ntptimeout
    ntptime.settime()
    #logger.debug(f"RTC set to {isotime()} from {ntpserver}")
    tt = time.time()
    #t = time.strftime("%Y-%m-%d %H:%M:%S", tt)
    logger.debug(f"RTC set to {tt} from {ntpserver}")

# def isotime(time_secs=None):
#     if time_secs is None:
#         if rtc is None:
#             return isotime(time.time())

#         # (year, month, day, weekday, hours, minutes, seconds, subseconds)
#         time_tuple = rtc.datetime()
#         return _ISO_FORMAT_STRING.format(
#             time_tuple[0],
#             time_tuple[1],
#             time_tuple[2],
#             time_tuple[4],
#             time_tuple[5],
#             time_tuple[6],
#             int(time_tuple[7] / 1000),
#         )
#     else:
#         # (year, month, mday, hour, minute, second, weekday, yearday)
#         time_tuple = time.localtime(time_secs)
#         return _ISO_FORMAT_STRING.format(
#             time_tuple[0],
#             time_tuple[1],
#             time_tuple[2],
#             time_tuple[3],
#             time_tuple[4],
#             time_tuple[5],
#             0,
#         )