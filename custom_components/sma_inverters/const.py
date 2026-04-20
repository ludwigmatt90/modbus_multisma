"""Constants for SMA Inverters integration."""

DOMAIN = "sma_inverters"
PLATFORMS = ["sensor"]

CONF_MQTT_HOST = "mqtt_host"
CONF_MQTT_PORT = "mqtt_port"
CONF_MQTT_USER = "mqtt_user"
CONF_MQTT_PASS = "mqtt_pass"
CONF_READ_INTERVAL = "read_interval"
CONF_WRITE_INTERVAL = "write_interval"
CONF_INVERTERS = "inverters"
CONF_RATE_LIMITS = "rate_limits"

DEFAULT_MQTT_PORT = 1883
DEFAULT_READ_INTERVAL = 10
DEFAULT_WRITE_INTERVAL = 60

MODBUS_SLAVE_ID = 3
REG_TOTAL_ENERGY_START = 30529
REG_SETPOINT = 40016

ATTR_NAME = "name"
ATTR_SECTION = "section"
ATTR_IP = "ip"

TOPIC_BASE = "sma/inverters"
TOPIC_APP = "sma/app"

PRIORITY_IMMEDIATE = 0
PRIORITY_INTERVAL = 1
