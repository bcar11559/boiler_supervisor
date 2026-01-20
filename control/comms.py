from initialise import is_micropython
import logging

logger = logging.getLogger(__name__)


if is_micropython():
    import machine
    import ubinascii
    import network
    from umqtt.simple import MQTTClient
    CLIENT_ID = ubinascii.hexlify(machine.unique_id())
    logger.info(f"(UMQTT) MQTT Client ID: {CLIENT_ID}")
else:
    import random
    import string
    from paho.mqtt import client as mqtt_client
    CLIENT_ID = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    FIRST_RECONNECT_DELAY = 1
    RECONNECT_RATE = 2
    MAX_RECONNECT_COUNT = 12
    MAX_RECONNECT_DELAY = 60
    logger.info(f"(PAHO) MQTT Client ID: {CLIENT_ID}")

import time
import json
from control.config import configuration as cfg

class MQTTConnection_x86:

    def __init__(self):

        self.client = mqtt_client.Client(client_id=CLIENT_ID, 
                                         callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)

        # client.username_pw_set(username, password)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.connect(cfg.mqtt_server, 
                            cfg.mqtt_port)
        self.client.loop_start()

    @staticmethod
    def on_connect(client, userdata, flags, rc, properties):
            if rc == 0:
                logger.info("Connected to MQTT Broker!")
            else:
                logger.info(f"Failed to connect MQTT, return code: {rc}")
    
    @staticmethod
    def on_disconnect(client, userdata, flags, rc, properties):
        logger.info(f"MQTT Disconnected with result code: {rc}")
        reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
        while reconnect_count < MAX_RECONNECT_COUNT:
            logger.info(f"MQTT Reconnecting in {reconnect_delay} seconds...")
            time.sleep(reconnect_delay)

            try:
                client.reconnect()
                logger.info("MQTT Reconnected successfully!")
                return
            except Exception as err:
                logger.error(f"MQTT {err}. Reconnect failed. Retrying...")

            reconnect_delay *= RECONNECT_RATE
            reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
            reconnect_count += 1
        logger.error(f"MQTT Reconnect failed after {reconnect_count} attempts. Exiting...")

    @staticmethod
    def decode_msg(msg, topic=None):
        msg_ = json.loads(msg.payload.decode())
        topic_ = msg.topic
        return msg_, topic_

    def receive(self):
        return

    def publish(self, topic, payload, qos=0):
        return self.client.publish(topic, payload, qos)

    def subscribe(self, topic, message_callback):
        self.client.subscribe(topic)
        self.client.on_message = message_callback

    def disconnect(self):
        self.client.disconnect()

class MQTTConnection_uP:

    def __init__(self, subscription_callback):
        
        self.client = MQTTClient(CLIENT_ID, 
                            cfg.mqtt_server, 
                            cfg.mqtt_port, 
                            cfg.mqtt_user, 
                            cfg.mqtt_password)
        self.client.set_callback(subscription_callback)
        self.client.connect()
        logger.info(f'MQTT Connected to MQTT Broker {cfg.mqtt_server}')

    @staticmethod
    def decode_msg(msg, topic):
        topic_ = topic.decode()
        msg_ = json.loads(msg.decode())
        return msg_, topic_

    def subscribe(self, topic):
        self.client.subscribe(topic)

    def receive(self):
        self.client.ping()
        self.client.check_msg()

    def publish(self, topic, payload, qos=0):
        self.client.publish(topic, payload, qos)
        
    def reconnect(self):
        logger.info(f'Failed to connect to MQTT broker {cfg.mqtt_server}, Reconnecting...')
        self.client.disconnect()
        time.sleep(5)
        self.client.connect()

    def disconnect(self):
        self.client.disconnect()

class WiFiConnection_x86:
    def __init__(self):
        return

    def connect(self):
        return True

    def status(self):
        return True
    
class WiFiConnection_uP:
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        network.hostname(f'esp32-{CLIENT_ID.decode()}')
        self.wlan.active(True)
        self.wlan.config(reconnects=5)

    def connect(self):
        logger.info(f'Connecting to WiFi SSID {cfg.ssid}')
        self.wlan.connect(cfg.ssid, cfg.password)

        timeout = cfg.wifitimeout
        while timeout > 0:
            if self.wlan.isconnected():          
                network_info = self.wlan.ifconfig()
                logger.info(f'Connection successful! IP address: {network_info[0]}')
                return True
            timeout -= 1
            logger.info('Waiting for Wi-Fi connection...')
            time.sleep(1)
        logger.error('Wi-Fi connection timeout...')
        return False

    def status(self):
        return self.wlan.isconnected()