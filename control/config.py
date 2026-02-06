import json

class Config:
    def __init__(self, config_file="site_config.json"):
        with open(config_file, "r") as f:
            self.data = json.load(f)
        
        #System Settings
        self.cycle_time = self.data["system"]["cycle_time"]
        self.ds18b20_pin = self.data["system"]["ds18b20_pin"]

        #WiFi Settings
        self.ssid = self.data["wifi"]["ssid"]
        self.password = self.data["wifi"]["password"]

        #MQTT Settings
        self.mqtt_server = self.data["mqtt"]["server"]
        self.mqtt_port = self.data["mqtt"]["port"]
        self.mqtt_user = self.data["mqtt"]["user"]
        self.mqtt_password = self.data["mqtt"]["password"]
        self.client_id = self.data["mqtt"]["client_id"]

        #Sensors
        self.sensors = self.data["sensors"]

configuration = Config()