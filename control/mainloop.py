from machine import Pin
import onewire, ds18x20
import time
import json
from control.config import configuration as cfg
from control.comms import initialise_wifi, connect_wifi, connect_mqtt, reconnect_mqtt, wifi_status
from boot import DEBUG

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
            "sensorID": self.id,
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

def main():
    # Add the sensors defined in the config file
    mons = []
    for skey, sval in cfg.sensors.items():
        if sval["type"] == "ds18b20":
            rom_code = sval["address"]
            id = skey
            if "topic" in sval:
                topic = sval["topic"]
            else:
                topic = None
            if "publish" in sval:
                publish = sval["publish"]
            else:
                publish = False
            mon = DS18X20Sensor(rom_code, id, topic=topic, publish=publish)
            mons.append(mon)

    # Connect to WiFi and MQTT
    wlan = initialise_wifi()
    connect_wifi(wlan)
    mqtt_client = connect_mqtt()
    
    # Main loop
    while True:
        for mon in mons:
            mon.check(mqtt_client)
            time.sleep(cfg.cycle_time)
        if not wifi_status(wlan):
            if DEBUG:
                print("DEBUG: WiFi disconnected, reconnecting...")
            connect_wifi(wlan)
            reconnect_mqtt(mqtt_client)
