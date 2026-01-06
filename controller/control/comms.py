import machine
import ubinascii
import network
import time
from umqtt.simple import MQTTClient

from control.config import configuration as cfg

CLIENT_ID = ubinascii.hexlify(machine.unique_id())

def connect_mqtt():
    print('Connected to MQTT Broker "%s"' % (cfg.mqtt_server))
    client = MQTTClient(CLIENT_ID, cfg.mqtt_server, cfg.mqtt_port, cfg.mqtt_user, cfg.mqtt_password)
    client.connect()
    return client

def reconnect_mqtt(client):
    print('Failed to connect to MQTT broker, Reconnecting...' % (cfg.mqtt_server))
    time.sleep(5)
    client.reconnect()

def initialise_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.hostname(f'esp32-{CLIENT_ID.decode()}')
    wlan.active(True)
    wlan.config(reconnects=5)
    return wlan

def connect_wifi(wlan):
    print('Connecting to WiFi SSID "%s"' % (cfg.ssid))
    wlan.connect(cfg.ssid, cfg.password)

    connection_timeout = 10
    while connection_timeout > 0:
        if wlan.connected():
            print('Connection successful!')
            network_info = wlan.ifconfig()
            print('IP address:', network_info[0])
            return True
        connection_timeout -= 1
        print('Waiting for Wi-Fi connection...')
        time.sleep(1)
    print('Wi-Fi connection timeout...')
    return False

def wifi_status(wlan):
    return wlan.isconnected()