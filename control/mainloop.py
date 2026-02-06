import time

from control.config import configuration as cfg
from control.signals import Signal
from control.comms import MQTTConnection_x86 as MQTTConnection
from control.comms import WiFiConnection_x86 as WiFiConnection
from initialise import is_micropython

import logging
logger = logging.getLogger(__name__)

wifi = WiFiConnection()
wifi.connect()
mqtt = MQTTConnection()
Signal.set_mqtt_connection(mqtt)

def main():
    try:
        i = 0
        while True:
            i+=1

            if is_micropython:
                pass
            else:
                if i > 2*60*60/cfg.cycle_time:
                    cfg.hc.em_setpoint()
                    i=0
                cfg.hc.em_inside_temp()
                logger.debug(str(cfg.hc))

            # Receive any updated subscribed values and then publish the 
            # latest values of all the signals.
            mqtt.receive()
            cfg.hc.update_values()
            Signal.publish_all()
            
            if not wifi.status():
                logger.info("WiFi disconnected, reconnecting...")
                wifi.connect()
                mqtt.reconnect()
            
            # OK as long as cycle_time >> time it takes to do everything else
            time.sleep(cfg.cycle_time)
    finally:
        mqtt.disconnect()