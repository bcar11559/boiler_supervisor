import time
from umqtt.simple import MQTTClient
from control.config import configuration as cfg

def connect():
    print('Connected to MQTT Broker "%s"' % (cfg.mqtt_server))
    client = MQTTClient(cfg.client_id, cfg.mqtt_server, cfg.mqtt_port, cfg.mqtt_user, cfg.mqtt_password)
    client.connect()
    return client

def reconnect():
    print('Failed to connect to MQTT broker, Reconnecting...' % (cfg.mqtt_server))
    time.sleep(5)
    client.reconnect()

try:
    client = connect()
except OSError as e:
    reconnect()