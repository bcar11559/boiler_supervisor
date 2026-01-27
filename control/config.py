import json
import logging
logger = logging.getLogger(__name__)

class ConfigurationError(Exception):

    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return f"{self.message}"

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

        # WiFi Settings
        try:
            wifi_settings = self.sys_settings["wifi"]
        except KeyError:
            msg = f"Configuration not valid! Configuration must contain an wifi settings entry."
            logging.exception(msg)
            raise ConfigurationError(msg)

        self.setval(wifi_settings, "ssid", "ssid", False)
        self.setval(wifi_settings, "password", "password", False)
        self.setval(wifi_settings, "timeout", "wifitimeout", True, default=10)

        # MQTT Settings
        try:
            self.mqtt_settings = self.sys_settings["mqtt"]
        except KeyError:
            msg = f"Configuration not valid! Configuration must contain an mqtt settings entry."
            logging.exception(msg)
            raise ConfigurationError(msg)

        self.setval(self.mqtt_settings, "mqtt_server", "mqtt_server", False)
        self.setval(self.mqtt_settings, "mqtt_port", "mqtt_port", False)
        self.setval(self.mqtt_settings, "mqtt_user", "mqtt_user", False)
        self.setval(self.mqtt_settings, "mqtt_password", "mqtt_password", False)
        self.setval(self.mqtt_settings, "client_id", "client_id", False)
        # Heating Controller and Measurement Unit Settings
        hc_settings =  self.data.get("heating_controller", None)
        mu_settings =  self.data.get("measurement_unit", None)

        self.hc = True if hc_settings else False
        self.mu = True if mu_settings else False

        if (not self.hc) and (not self.mu):
            msg = f"Configuration not valid! Configuration must contain either a Heating Controller or a Measurement Unit or both."
            logging.exception(msg)
            raise ConfigurationError(msg) 

        # Heating Controller
        if self.hc:
            self.setval(self.hc, "outside_temp_remote", "outside_temp_remote", False)
            self.setval(self.hc, "outside_temp_local_meas", "outside_temp_local_meas", False)
            self.setval(self.hc, "inside_temp_apparent", "inside_temp_apparent", False)
            self.setval(self.hc, "wind_speed", "wind_speed", False)
            self.setval(self.hc, "wind_dir", "wind_dir", False)
            self.setval(self.hc, "solar_gain", "solar_gain", False)

            if not self.hc.outside_temp_remote:
                msg = "Heating Controller must have outside_temp_remote signal configured."
            elif not self.hc.outside_temp_local_meas:
                msg = "Heating Controller must have outside_temp_local_meas signal configured." 
                logging.exception(msg)
                raise ConfigurationError(msg)      
            
        # Measurement Unit Settings
        if self.mu:
            self.setval(self.mu, "signals", "signals", True, default={})
            self.setval(self.mu, "ds18b20_pin", "ds18b20_pin", True, default=2)
        
    def setval(self, lookup, val, attr, optional, default=None):

        if lookup.get(val, None) is None and (not optional):
            msg = f"Configuration item {val} is not optional! Item must be configured."
            logging.exception(msg)
            raise ConfigurationError(msg)    

        value = lookup.get(val, default)
        setattr(self, attr, value)

configuration = Config()