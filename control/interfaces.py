import logging
logger = logging.getLogger(__name__)

import json
try:
    from control.initialise import is_micropython
except ImportError:
    is_micropython = False


if is_micropython:
    from machine import Pin
    import onewire, ds18x20
    DS18X20TempInterface.scan()
else:
    import random


class Interface:

    interfaces = []

    def __init__(self, id, typ):
        self.id = id
        self.typ = typ
        self._values = {}

    @property
    def values(self):
        return self._values
    
    @values.setter
    def values(self, val):
        self._values = val

    @property
    def payload(self):
        return {
            "signalID": self.id,
            "values": self.values,
            }

class DS18X20TempInterface(Interface):
    
    roms = {}
    pin_number = 2
    em_baseline_temp = 18
    em_temp_span = 4

    def __init__(self, id, rom_code, typ):
        super().__init__(id, typ)
        self.rom_code = rom_code
    
    @classmethod
    def scan(cls):
        '''
        Scan for connected DS18B20 devices and return their ROM codes.
        '''
        if is_micropython:
            devices = ds18x20.DS18X20(onewire.OneWire(Pin(cls.pin_number))).scan()
        else:
            # Emulated environment: return a fake set
            devices = ['230056789ab', '23009abcdef0']

        cls.roms = {rom.hex(): rom for rom in devices}
        logger.info(f"Connected DS18B20 devices: {cls.roms}")
        return cls.roms

    @property
    def values(self):
        if is_micropython:
            for rom_code, rom in self.roms.items():
                if rom_code == self.rom_code:
                    self.ds.convert_temp()
                    return self.ds.read_temp(rom)
        else:
            inc = random.random()*self.em_temp_span
            return self.em_baseline_temp + inc

    @property
    def payload(self):
        pyl = super().payload
        pyl.update({"sensorROM": self.rom_code})
        return pyl

class MQTTInterface(Interface):
    mqtt_connection = None
    subscribed_topics = []

    @classmethod
    def set_mqtt_connection(cls, mqtt):
        cls.mqtt_connection = mqtt
    
    @classmethod
    def add_subscribe_topic(cls, topic):
        if topic not in cls.subscribed_topics:
            cls.subscribed_topics.append(topic)

    @classmethod
    def get_interface(cls, id):
        for interface in cls.interfaces:
            if interface.id == id:
                return interface
    
    @classmethod
    def update_interface(cls, id, values):
        interface = cls.get_interface(id)
        if interface:
            interface.values = values

    @classmethod
    def publish_all(cls):
        for interface in cls.interfaces:
            interface.publish()

    def __init__(self, id, typ, 
                 publish_topic=None, 
                 subscribe_topic=None):
        super().__init__(id, typ)
        self.publish_topic = publish_topic
        self.subscribe_topic = subscribe_topic
        
        if subscribe_topic:
            self.add_subscribed_topic(subscribe_topic)
        self.interfaces.append(self)
    
    def publish(self, qos=0):
        if not self.publish_topic:
            return
        if not self.mqtt_connection:
            return
        self.mqtt_connection.publish(self.publish_topic, 
                                     json.dumps(self.payload), 
                                     qos)


if __name__ == "__main__":
    s1 = Interface("test")
    print(s1.payload)

    s2 = DS18X20TempInterface("test2", "nkjf933ii")
    print(s2.payload)

    mqtt = MQTTConnection()

    MQTTInterface.set_mqtt_connection()

    mqtt.receive()
    
    



    MQTTInterface.publish_all()

