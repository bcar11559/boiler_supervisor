import time
import random
from datetime import datetime
import logging

import numpy as np

from control.config import configuration as cfg
from control.signals import Signal, MQTTSignal, OutputSignal
from control.components import HeatingController
from control.comms import MQTTConnection_x86 as MQTTConnection
from control.comms import WiFiConnection_x86 as WiFiConnection

logger = logging.getLogger(__name__)

global signals
global subscribed_topics

signals = []
subscribed_topics = []
# Attach the main process signals

# otl_signal = Signal(cfg.signals.get("outside_temp_local"))
# cfg.signals.get("inside_temp")
# cfg.signals.get("solar_gain")
# cfg.signals.get("outside_temp_remote")
# cfg.signals.get("heating_controller")


for id, vals in cfg.signals.items():

    sigtype = vals.get("type")

    if sigtype == "ds18b20":
        signal = None
        continue
        signal = DS18X20Signal(id, 
                               sigtype, 
                               vals.get("address"), 
                               publish_topic=vals.get("publish_topic"))
        
    if sigtype in ["mqtt-input", "mqtt-output"]:
        topic = vals.get("subscribe_topic")
        if topic:
            subscribed_topics.append(topic)
        signal = MQTTSignal(id,
                            sigtype,
                            vals.get("mapping", {}),
                            publish_topic=vals.get("publish_topic"),
                            subscribe_topic=vals.get("subscribe_topic"))
    
    if sigtype == "hc":
        # Initialise the controller
        outside_temp = 0.1
        outside_temp_remote = -1.1
        outside_temp_remote_wchill = -8
        winddir = 100
        inside_temp = 21
        setpoint = 18
        hc = HeatingController(
            id,
            outside_temp, 
            outside_temp_remote, 
            outside_temp_remote_wchill, 
            winddir, 
            inside_temp,
            setpoint)
        hc.signal = OutputSignal(id, hc, sigtype, publish_topic=vals.get("publish_topic"))
        signal = hc.signal

    if signal:
        signals.append(signal)

subscribed_topics = list(set(subscribed_topics))


def on_message(client, userdata, msg):

    msg_, topic_ = MQTTConnection.decode_msg(msg)
    thissignal = None

    for signal in signals:
        if topic_ == signal.subscribe_topic:
            if msg_["signalID"] == signal.id:
                thissignal = signal
                break
    
    if not thissignal:
        return

    for key, value in msg_.items():
        if key == "signalID":
            continue
        setattr(thissignal, key, value)

    # if thissignal.id == "smhi_134110":
    #     s = thissignal
    #     print(f"Updated vals @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {s.temperature}, {s.windChill} {s.windDirection}") 

wifi = WiFiConnection()
wifi.connect()
mqtt = MQTTConnection()
for topic in subscribed_topics:
    mqtt.subscribe(topic, on_message)
for signal in signals:
    signal.set_mqtt_connection(mqtt)

def calculate_input_power(Pnom, t_room, t_flow, delta_t=10):
    t_return = t_flow - delta_t
    dTln = (t_flow - t_return) / np.log((t_flow-t_room)/(t_return-t_room)) 
    return Pnom * (dTln / 49.83289) ** 1.3


def main():
    try:
        i = 0
        while True:
            i+=1

            if i > 2*60*60/cfg.cycle_time:
                i=0
                r = random.random()*4
                hc.setpoint = 18 + r

            Ploss = (hc.inside_temp-hc.outside_temp_remote_wchill)*150
            Pi = calculate_input_power(15000, hc.inside_temp, hc.flow_temp)
            diff_gain = (Pi - Ploss)*0.0001

            hc.inside_temp += diff_gain
            logger.debug(f"ft={hc.flow_temp:.2f}, sp={hc.setpoint:.2f}, it={hc.inside_temp:.2f}, loss={Ploss:.2f}, ip={Pi:.2f}, dg={diff_gain:.2f}")

            # Receive any updated subscribed values, do the control calculation
            # and then publish the latest values of all the signals.
            mqtt.receive()

            update = False
            for signal in signals:
                if signal.id == "smhi_134110":
                    if (signal.temperature is not None) and (signal.temperature != hc.outside_temp_remote):
                        hc.outside_temp_remote = signal.temperature
                        update = True
                    if (signal.windChill is not None) and (signal.windChill != hc.outside_temp_remote_wchill):
                        hc.outside_temp_remote_wchill = signal.windChill
                        update = True
                    if (signal.windDirection is not None) and (signal.windDirection != hc.winddir):
                        hc.winddir = signal.windDirection
                        update = True
                    if update:
                        logger.debug(f"Updated controller vals: ot={hc.outside_temp_remote}, wchill={hc.outside_temp_remote_wchill} winddir={hc.winddir}")
                        update = False

            for signal in signals:
                signal.publish()
            
            if not wifi.status():
                logger.info("WiFi disconnected, reconnecting...")
                wifi.connect()
                mqtt.reconnect()
            
            # OK as long as cycle_time >> time it takes to do everything else
            time.sleep(cfg.cycle_time)
    finally:
        mqtt.disconnect()