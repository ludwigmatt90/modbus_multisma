"""Config flow for SMA Inverters integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_MQTT_HOST,
    CONF_MQTT_PORT,
    CONF_MQTT_USER,
    CONF_MQTT_PASS,
    CONF_READ_INTERVAL,
    CONF_WRITE_INTERVAL,
    CONF_INVERTERS,
    DEFAULT_MQTT_PORT,
    DEFAULT_READ_INTERVAL,
    DEFAULT_WRITE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_MQTT_HOST): str,
        vol.Optional(CONF_MQTT_PORT, default=DEFAULT_MQTT_PORT): int,
        vol.Optional(CONF_MQTT_USER, default=""): str,
        vol.Optional(CONF_MQTT_PASS, default=""): str,
        vol.Optional(CONF_READ_INTERVAL, default=DEFAULT_READ_INTERVAL): int,
        vol.Optional(CONF_WRITE_INTERVAL, default=DEFAULT_WRITE_INTERVAL): int,
    }
)


class SmaInvertersConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SMA Inverters."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            self._data.setdefault(CONF_INVERTERS, [])
            return self.async_create_entry(
                title=f"SMA Inverters ({user_input[CONF_MQTT_HOST]})",
                data=self._data,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> SmaInvertersOptionsFlow:
        """Return the options flow."""
        return SmaInvertersOptionsFlow(config_entry)


class SmaInvertersOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for SMA Inverters."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self._config_entry.data

        options_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_READ_INTERVAL,
                    default=current.get(CONF_READ_INTERVAL, DEFAULT_READ_INTERVAL),
                ): int,
                vol.Optional(
                    CONF_WRITE_INTERVAL,
                    default=current.get(CONF_WRITE_INTERVAL, DEFAULT_WRITE_INTERVAL),
                ): int,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            errors=errors,
        )
