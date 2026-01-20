import logging
logger = logging.getLogger(__name__)

import json

from initialise import is_micropython

if is_micropython():
    from machine import Pin
    import onewire, ds18x20
else:
    pass

from control.config import configuration as cfg

class Signal:
    def __init__(self, id, sigtype, publish_topic=None, subscribe_topic=None):
        self.id = id
        self.sigtype = sigtype
        self.publish_topic = publish_topic
        self.subscribe_topic = subscribe_topic
        self.mqtt = None

    def set_mqtt_connection(self, mqtt):
        self.mqtt = mqtt

    def __publish__(self, payload, qos=0):
        if not self.publish_topic:
            return
        pyl = json.dumps(payload)
        if self.mqtt:
            self.mqtt.publish(self.publish_topic, pyl, qos)

class OutputSignal(Signal):
    def __init__(self, id, owner, sigtype, publish_topic=None):
        super().__init__(id, sigtype, publish_topic, subscribe_topic=None)
        self.owner = owner

    def publish(self):
        self.__publish__(self.owner.payload)

class MQTTSignal(Signal):
    def __init__(self, id, sigtype, mapping, publish_topic=None, subscribe_topic=None):
        super().__init__(id, sigtype, publish_topic, subscribe_topic)
        self.set_mapping(mapping)
    
    def publish(self):
        pass
    
    def set_mapping(self, mapping):
        for k, _ in mapping.items():
            setattr(self, k, None) 


class DS18X20Signal(Signal):
    
    if is_micropython():
        ow = onewire.OneWire(Pin(cfg.ds18b20_pin))
        ds = ds18x20.DS18X20(ow)
        alldevices = {rom.hex(): rom for rom in ds.scan()}
        logger.info(f"Found local DS18B20 devices: {alldevices}")
    else:
        pass

    def __init__(self, id, sigtype, rom_code, publish_topic=None, subscribe_topic=None):
        super().__init__(id, sigtype, publish_topic, subscribe_topic)
        self.rom_code = rom_code
        self.temp = self.get_temp()

    def get_temp(self):
        for rom_code, rom in DS18X20Signal.alldevices.items():
            if rom_code == self.rom_code:
                DS18X20Signal.ds.convert_temp()
                self.temp = DS18X20Signal.ds.read_temp(rom)
                return self.temp

    def publish(self):
        self.get_temp()
        payload = {
            "signalID": self.id,
            "sensorROM": self.rom_code,
            "temperature": self.temp,
            }
        logger.debug(f"DEBUG: Temp1 {self.temp:.1f}°C | Sensor {self.id}")
        self.__publish__(payload)

