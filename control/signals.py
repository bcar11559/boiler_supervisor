import logging
logger = logging.getLogger(__name__)

import json
from control.interfaces import Sensor, DS18X20Sensor
from control.exceptions import SignalError

SUPPORTED_SIG_TYPES = ["ds18b20", "mqtt", "ntc450"]

def make_signal(id, sigspec, source=None):

    # Validate the sigspec entry
    if (not type(sigspec) is dict):
        msg = "Signal specification argument is not a dictionary!"
        logger.exception(msg)
        raise SignalError(msg)

    sigtype =  sigspec.get("type", None)

    if sigtype not in SUPPORTED_SIG_TYPES:
        if sigtype is None:
            msg = f"Signal type must be specified!"
        else:
            msg = f"Signal type {sigtype} not supported!"
        logger.exception(msg)
        raise SignalError(msg)

    sigid =  sigspec.get("signalID", None)

    if sigid is None:
        msg = f"Signal id must be specified!"
        logger.exception(msg)
        raise SignalError(msg)

    publish_topic =  sigspec.get("publish_topic", None)

    if publish_topic is None:
        msg = f"Signal publish_topic must be specified!"
        logger.exception(msg)
        raise SignalError(msg)
    
    # Create the signal
    if sigtype == "ds18b20":
        rom_code = sigspec.get("signalID", None)
        if not rom_code:
            msg = f"DS18B20 signal must have a signalID (ROM code) specified!"
            logger.exception(msg)
            raise SignalError(msg)
        if not source:
            source =  DS18X20Sensor(id, rom_code)
        return Signal(id, sigspec, source)

    if sigtype == "ntc450":
        source =  Sensor(id)
        return Signal(id, sigspec, source)

    # Create the signal
    if sigtype == "mqtt":
        subscribe_topic =  sigspec.get("subscribe_topic", None)
        if not subscribe_topic:
            msg = f"MQTT signal must have a subscribe_topic specified!"
            logger.exception(msg)
            raise SignalError(msg)
        if not source:
            msg = f"Source argument must be supplied for MQTT Signals!"
            logger.exception(msg)
            raise SignalError(msg)
        return Signal(id, sigspec, source)

class Signal:

    mqtt = None
    all_signals = []
    subscribed_topics = []

    def __init__(self, id, sigspec, source):
        self.id = id
        self.sigtype = sigspec.get("type")
        self.publish_topic = sigspec.get("publish_topic")
        self.source = source
        Signal.all_signals.append(self)
        self.subscribe_topic = sigspec.get("subscribe_topic")
        Signal.add_subscribed_topic(sigspec.get("subscribe_topic"))

    @classmethod
    def set_mqtt_connection(cls, mqtt):
        cls.mqtt = mqtt

    @classmethod
    def publish_all(cls):
        for signal in cls.all_signals:
            signal.publish()

    @classmethod
    def get_signal_with_id(cls, id):
        for signal in cls.all_signals:
            if signal.id == id:
                return signal
    
    @classmethod
    def update_signal_with_id(cls, id, msg_):
        signal = cls.get_signal_with_id(id)
        if signal:
            for key, value in msg_.items():
                if key == "signalID":
                    continue
                print(1, key, value)
                setattr(signal, key, value)

    @classmethod
    def add_subscribed_topic(cls, topic):
        if topic not in cls.subscribed_topics:
            cls.subscribed_topics.append(topic)
    
    # @classmethod
    # def get_signals_with_topic(cls, topic):
    #     signals = []
    #     for signal in Signal.all_signals:
    #         if isinstance(signal, cls):
    #             if signal.subscribe_topic == topic:
    #                 signals.append(signal)
    #     return signals

    def publish(self):
        if not self.source:
            return
        self.__publish__(self.source.payload)

    def __publish__(self,  payload, qos=0):
        if not self.publish_topic:
            return
        pyl = json.dumps(payload)
        if Signal.mqtt:
            Signal.mqtt.publish(self.publish_topic, pyl, qos)






