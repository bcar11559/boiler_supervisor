import json
import logging
logger = logging.getLogger(__name__)

from control.signals import make_signal
from control.components import HeatingController
from control.interfaces import DS18X20Sensor
from control.exceptions import ConfigurationError

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
        DS18X20Sensor.pin_number = self.ds18b20_pin
        HeatingController.cycle_time = self.cycle_time

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
        self.setval(self.mqtt_settings, "mqtt_client_id", "mqtt_client_id", False)
        
        # Heating Controller and Measurement Unit Settings
        hc_settings =  self.data.get("heating_controller", None)
        mu_settings =  self.data.get("measurement_unit", None)

        self.hc = True if hc_settings else False
        self.mu = True if mu_settings else False

        if (not self.hc) and (not self.mu):
            msg = f"Configuration not valid! Configuration must contain either a Heating Controller or a Measurement Unit or both."
            logging.exception(msg)
            raise ConfigurationError(msg) 

        self.mu_signals = mu_settings.get("signals", None)

        for signame, sigspec in self.mu_signals.items():
            make_signal(signame, sigspec)

        hc_signals = hc_settings.get("signals", None)
        if hc_signals is None:
            msg = "Heating Controller must have signals configured."
            logging.exception(msg)
            raise ConfigurationError(msg)   
        
        # Heating Controller
        if self.hc:
            self.hc = HeatingController()

            if not hc_signals.get("outside_temp_remote", None):
                msg = "Heating Controller must have outside_temp_remote signal configured."
            elif not hc_signals.get("outside_temp_local", None):
                msg = "Heating Controller must have outside_temp_local signal configured." 
                logging.exception(msg)
                raise ConfigurationError(msg)
            
            for s in HeatingController.alias_mapping.keys():
                sig = hc_signals.get(s, None)
                if sig:
                    alias = sig.get("alias", None)
                    if alias:                    
                        HeatingController.alias_mapping[s] = sig["alias"]
                    make_signal(s, sig, self.hc)
        
    def setval(self, lookup, val, attr, optional, default=None):

        if lookup.get(val, None) is None and (not optional):
            msg = f"Configuration item {val} is not optional! Item must be configured."
            logging.exception(msg)
            raise ConfigurationError(msg)    

        value = lookup.get(val, default)
        setattr(self, attr, value)

configuration = Config()