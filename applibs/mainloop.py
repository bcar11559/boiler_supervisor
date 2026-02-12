from applibs.logger import ApplicationLogger
logger = ApplicationLogger.logger

import time

from neopixel import NeoPixel
from machine import Pin
led_pin = Pin(8, Pin.OUT)
np = NeoPixel(led_pin, 1)

def maintest_rgb_blink():
    np[0] = (255,0,0)
    np.write()
    time.sleep(1)
    np[0] = (0,255,0)
    np.write()
    time.sleep(1)
    np[0] = (0,0,255)
    np.write()
    time.sleep(1)

def maintest_20s_fallout():
    for i in range(20):
        time.sleep(1)
        print(f"Hello World {i}!")


# from applibs.config import configuration as cfg
# from applibs.comms import initialise_wifi, connect_wifi, connect_mqtt, reconnect_mqtt, wifi_connected

# def maintest_tempmeas():
#     # Add the sensors defined in the config file
#     mons = []
#     for skey, sval in cfg.sensors.items():
#         if sval["type"] == "ds18b20":
#             rom_code = sval["address"]
#             id = skey
#             if "topic" in sval:
#                 topic = sval["topic"]
#             else:
#                 topic = None
#             if "publish" in sval:
#                 publish = sval["publish"]
#             else:
#                 publish = False
#             mon = DS18X20Sensor(rom_code, id, topic=topic, publish=publish)
#             mons.append(mon)

#     # Connect to WiFi and MQTT
#     wlan = initialise_wifi()
#     connect_wifi(wlan)

#     # This won't work since mqtt_client will not be defined if connect_mqtt fails
#     try:
#         mqtt_client = connect_mqtt()
#     except OSError as e:
#         reconnect_mqtt(mqtt_client)

#     # Main loop
#     while True:
#         for mon in mons:
#             mon.check(mqtt_client)
#             time.sleep(cfg.cycle_time)
#             print("hej")
#         if not wifi_connected(wlan):
#             if DEBUG:
#                 print("DEBUG: WiFi disconnected, reconnecting...")
#             connect_wifi(wlan)
        