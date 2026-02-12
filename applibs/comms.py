from applibs.logger import ApplicationLogger
logger = ApplicationLogger.logger

import machine
import network
import time
import usocket as socket
import ubinascii as binascii

from umqtt.simple import MQTTClient

from applibs.config import configuration as cfg

DEBUG = True

CLIENT_ID = binascii.hexlify(machine.unique_id())

def connect_mqtt():
    print('Connected to MQTT Broker "%s"' % (cfg.mqtt_server))
    client = MQTTClient(CLIENT_ID, cfg.mqtt_server, cfg.mqtt_port, cfg.mqtt_user, cfg.mqtt_password)
    client.connect()
    return client

def reconnect_mqtt(client):
    if DEBUG:
        print('Failed to connect to MQTT broker, Reconnecting...' % (cfg.mqtt_server))
    time.sleep(5)
    client.reconnect()

def initialise_wifi(host=f'esp32-{CLIENT_ID.decode()}', reconnects=-1):
    wlan = network.WLAN(network.STA_IF)
    network.hostname(host)
    wlan.active(True)
    logger.info(f'WiFi radio <ON> with hostname: {host}')
    wlan.config(reconnects=reconnects)
    return wlan

def connect_wifi(wlan):
    logger.info(f'Trying to connect to WiFi SSID: {cfg.ssid}')
    wlan.connect(cfg.ssid, cfg.password)
    time.sleep(1)

    timeout = 10
    while timeout > 0:
        if wlan.isconnected():          
            network_info = wlan.ifconfig()
            logger.info(f'Wi-Fi connected. Assigned IP address: {network_info[0]}')
            return True
        timeout -= 1
        logger.info(f'Waiting for Wi-Fi connection... {timeout}')
        time.sleep(1)
    
    logger.info(f'Wi-Fi connection failed... {timeout}')
    return False

def wifi_connected(wlan):
    return wlan.isconnected()

def wan_ok(host='1.1.1.1', port=53, timeout=3):
    """
    Checks to see if an external WAN host can be resolved.
    i.e. if the public internet can be reached.
    """
    try:
        sock = socket.socket()
        sock.settimeout(timeout)
        addr = socket.getaddrinfo(host, port)[0][-1]
        sock.connect(addr)
        logger.debug(f'WAN OK, was able to reach {host}')
        return True
    except Exception as e:
        logger.exception(e)
        return False