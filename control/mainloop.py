import time

from control.config import configuration as cfg
from control.signals import Signal, make_signal
from control.components import HeatingController
from control.comms import MQTTConnection_x86 as MQTTConnection
from control.comms import WiFiConnection_x86 as WiFiConnection
from initialise import is_micropython

import logging
logger = logging.getLogger(__name__)

# Setup the measurement unit signals.
if cfg.mu:
    for signame, sigspec in cfg.mu.signals.items():
        make_signal(signame, sigspec)

# Setup the heating controller signals.
if cfg.hc:
    hc = HeatingController()
    for signame, sigspec in cfg.hc.signals.items():
        make_signal(signame, sigspec, hc)       

wifi = WiFiConnection()
wifi.connect()
mqtt = MQTTConnection()
Signal.set_mqtt_connection(mqtt)

def main():
    try:
        i = 0
        while True:
            i+=1

            if is_micropython():
                pass
            else:
                if i > 2*60*60/cfg.cycle_time:
                    hc.em_setpoint()
                    i=0
                hc.em_inside_temp()
                msg = f"ft={hc.flow_temp:.2f}, sp={hc.setpoint:.2f}, it={hc.inside_temp:.2f}, loss={hc.em_ploss:.2f}, ip={hc.em_input_power:.2f}, dg={hc.em_diff_gain:.2f}"
                logger.debug(msg)

            # Receive any updated subscribed values and then publish the 
            # latest values of all the signals.
            mqtt.receive()
            hc.update_values()
            Signal.publish_all()
            
            if not wifi.status():
                logger.info("WiFi disconnected, reconnecting...")
                wifi.connect()
                mqtt.reconnect()
            
            # OK as long as cycle_time >> time it takes to do everything else
            time.sleep(cfg.cycle_time)
    finally:
        mqtt.disconnect()