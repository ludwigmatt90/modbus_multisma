"""Constants for SMA Inverters integration."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "sma_inverters"
ATTRIBUTION = "Data provided by SMA Solar inverters via Modbus TCP"

# Config keys
CONF_INVERTERS = "inverters"
CONF_HOST = "host"
CONF_PORT = "port"
CONF_SLAVE_ID = "slave_id"
CONF_SCAN_INTERVAL = "scan_interval"

# Inverter config keys
CONF_INVERTER_NAME = "name"
CONF_INVERTER_SECTION = "section"
CONF_INVERTER_HOST = "host"
CONF_INVERTER_PORT = "port"
CONF_INVERTER_SLAVE_ID = "slave_id"

# Defaults
DEFAULT_PORT = 502
DEFAULT_SLAVE_ID = 3
DEFAULT_SCAN_INTERVAL = 30  # seconds

# Modbus register addresses
REG_TOTAL_ENERGY_START = 30529  # kWh (scaled x 1000 → Wh)
REG_CURRENT_POWER = 30775       # Watts AC power output

# Modbus settings
MODBUS_TIMEOUT = 10  # seconds
