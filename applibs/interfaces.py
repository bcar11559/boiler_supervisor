from machine import Pin
import onewire, ds18x20

import json

from micropython import const

DEBUG = const(True)

from applibs.config import configuration as cfg

class DS18X20Sensor:
    ow = onewire.OneWire(Pin(cfg.ds18b20_pin))
    ds = ds18x20.DS18X20(ow)
    alldevices = {rom.hex(): rom for rom in ds.scan()}
    print("Found local DS18B20 devices:", alldevices)

    def __init__(self, rom_code, id, topic=None, publish=False):
        self.rom_code = rom_code
        self.id = id
        self.topic = topic
        self.publish = publish

    def get_temp(self):
        for rom_code, rom in DS18X20Sensor.alldevices.items():
            if rom_code == self.rom_code:
                DS18X20Sensor.ds.convert_temp()
                return DS18X20Sensor.ds.read_temp(rom)

    def check(self, mqtt_client):
        temp = self.get_temp()
        payload = {
            "signalID": self.id,
            "sensorROM": self.rom_code,
            "temperature": temp,
            }
        if DEBUG:
            print(f"DEBUG: Temp1 {temp:.1f}°C | Sensor {self.id}")
        if self.publish:
            self.__publish__(mqtt_client, payload)

    def __publish__(self, mqtt_client, payload, qos=0):
        if not self.topic:
            if DEBUG:
                print("DEBUG: No topic defined, not publishing")
            return
        pyl = json.dumps(payload)
        mqtt_client.publish(self.topic, pyl, qos)