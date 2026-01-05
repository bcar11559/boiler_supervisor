from machine import Pin
import onewire, ds18x20
import time
import json
from control.mqtt import client
from control.config import configuration as cfg

class DS18X20Sensor:
    ow = onewire.OneWire(Pin(cfg.ds18b20_pin))
    ds = ds18x20.DS18X20(ow)
    alldevices = {rom.hex(): rom for rom in ds.scan()}
    print("DEBUG: Found local DS18B20 devices:", alldevices)

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

    def check(self):
        temp = self.get_temp()
        payload = {
            "sensorID": self.id,
            "sensorROM": self.rom_code,
            "temperature": temp,
            }
        print(f"DEBUG: Temp1 {temp:.1f}°C | Sensor {self.id}")
        if self.publish:
            self.__publish__(payload)

    def __publish__(self,  payload, qos=0):
        if not self.topic:
            print("DEBUG: No topic defined, not publishing")
            return
        pyl = json.dumps(payload)
        client.publish(self.topic, pyl, qos)

def main():
    # Add the sensors defined in the config file
    mons = []
    for sensor in cfg.sensors:
        if sensor["type"] == "DS18X20":
            rom_code = sensor["address"]
            id = sensor
            if "topic" in sensor:
                topic = sensor["topic"]
            else:
                topic = None
            if "publish" in sensor:
                publish = sensor["publish"]
            else:
                publish = False
            mon = DS18X20Sensor(rom_code, id, topic=topic, publish=publish)
            mons.append(mon)

    # Main loop
    while True:
        for mon in mons:
            mon.check()
            time.sleep(cfg.cycle_time)
