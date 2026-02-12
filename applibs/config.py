from applibs.logger import ApplicationLogger
logger = ApplicationLogger.logger

import json
from applibs.exceptions import ConfigurationError

class Config:
    def __init__(self, config_file="site_config.json"):

        with open(config_file, "r") as f:
            self.data = json.load(f)
        
        # System Settings
        try:
            self.sys_settings = self.data["system"]
        except KeyError:
            msg = f"Configuration not valid! Configuration must contain a sytem settings entry."
            logging.exception(msg)
            raise ConfigurationError(msg)

        self.setval(self.sys_settings, "cycle_time", "cycle_time", True, default=5)
        self.setval(self.sys_settings, "ds18b20_pin", "ds18b20_pin", True, default=2)

        # WiFi Settings
        try:
            wifi_settings = self.sys_settings["wifi"]
        except KeyError:
            msg = f"Configuration not valid! System settings must contain an wifi settings entry."
            logging.exception(msg)
            raise ConfigurationError(msg)

        self.setval(wifi_settings, "ssid", "ssid", False)
        self.setval(wifi_settings, "password", "password", False)
        self.setval(wifi_settings, "timeout", "wifitimeout", True, default=10)

        # MQTT Settings
        try:
            self.mqtt_settings = self.sys_settings["mqtt"]
        except KeyError:
            msg = f"Configuration not valid! System settings must contain an mqtt settings entry."
            logging.exception(msg)
            raise ConfigurationError(msg)

        self.setval(self.mqtt_settings, "mqtt_server", "mqtt_server", False)
        self.setval(self.mqtt_settings, "mqtt_port", "mqtt_port", True, default=1883)
        self.setval(self.mqtt_settings, "mqtt_user", "mqtt_user", True, default="")
        self.setval(self.mqtt_settings, "mqtt_password", "mqtt_password", True, default="")
        #self.setval(self.mqtt_settings, "mqtt_client_id", "mqtt_client_id", False)
      
    def setval(self, lookup, val, attr, optional, default=None):

        if lookup.get(val, None) is None and (not optional):
            msg = f"Configuration item {val} is not optional! Item must be configured."
            logging.exception(msg)
            raise ConfigurationError(msg)    

        value = lookup.get(val, default)
        setattr(self, attr, value)

configuration = Config()