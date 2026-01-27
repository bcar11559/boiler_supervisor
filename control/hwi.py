import logging
logger = logging.getLogger(__name__)

from control.config import configuration as cfg
from initialise import is_micropython

if is_micropython():
    from machine import Pin
    import onewire, ds18x20
else:
    import random

class DS18X20Sensor:
    
    roms = {}
    em_baseline_temp = 18
    em_temp_span = 4

    def __init__(self, id, rom_code):
        self.id = id
        self.rom_code = rom_code
    
    @classmethod
    def scan_devices(cls):
        '''
        Scan for connected DS18B20 devices and return their ROM codes.
        '''
        if is_micropython():
            pin_number = cfg.mu_settings.ds18b20_pin
            devices = ds18x20.DS18X20(onewire.OneWire(Pin(pin_number))).scan()
        else:
            # Emulated environment: return a fake set
            devices = ['230056789ab', '23009abcdef0']

        cls.roms = {rom.hex(): rom for rom in devices}
        logger.info(f"Connected DS18B20 devices: {cls.roms}")
        return cls.roms

    @property
    def temp(self):
        if is_micropython():
            for rom_code, rom in DS18X20Sensor.roms.items():
                if rom_code == self.rom_code:
                    DS18X20Sensor.ds.convert_temp()
                    return DS18X20Sensor.ds.read_temp(rom)
        else:
            inc = random.random()*DS18X20Sensor.em_temp_span
            return DS18X20Sensor.em_baseline_temp + inc

    @property
    def payload(self):
        return {
            "signalID": self.id,
            "sensorROM": self.rom_code,
            "temperature": self.temp,
            }
