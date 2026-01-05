# boot.py -- run on boot-up
VERSION = "dev0.0.1"
print(f'Booting: Firmware version {VERSION}')

import network
from control.config import configuration as cfg

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(cfg.ssid, cfg.password)
while station.isconnected() == False:
  pass
print('Connection successful')