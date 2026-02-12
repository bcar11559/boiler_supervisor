## Intro

Micropython application for supervision and control of heat exchangers.

Built for ESP32S3 microcontroller cards.
MQTT based communication over WiFi LAN.

## Setup

Create a local file called "site_config.json" in the same directory as boot.py.

{
    "system" : {
        "wifi" : {
            "ssid" : "my_SSID",
            "password" : "my_PASSWORD"
        },
        "mqtt": {
            "mqtt_server" : "my_BROKER"
        }
    }
}
