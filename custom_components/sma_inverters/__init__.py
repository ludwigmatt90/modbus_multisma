"""SMA Inverters integration for Home Assistant."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    CONF_INVERTERS,
    CONF_MQTT_HOST,
    CONF_MQTT_PORT,
    CONF_MQTT_USER,
    CONF_MQTT_PASS,
    CONF_READ_INTERVAL,
    CONF_WRITE_INTERVAL,
)
from .inverter import Inverter

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SMA Inverters from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    inverters: list[Inverter] = [
        Inverter(
            name=inv["name"],
            section=inv["section"],
            ip=inv["ip"],
        )
        for inv in entry.data.get(CONF_INVERTERS, [])
    ]

    hass.data[DOMAIN][entry.entry_id] = {
        "inverters": inverters,
        "mqtt_host": entry.data.get(CONF_MQTT_HOST),
        "mqtt_port": entry.data.get(CONF_MQTT_PORT),
        "mqtt_user": entry.data.get(CONF_MQTT_USER),
        "mqtt_pass": entry.data.get(CONF_MQTT_PASS),
        "read_interval": entry.data.get(CONF_READ_INTERVAL),
        "write_interval": entry.data.get(CONF_WRITE_INTERVAL),
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
