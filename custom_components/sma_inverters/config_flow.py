"""Config flow for the SMA Inverters integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .api import (
    SmaInverterApiClient,
    SmaInverterApiClientCommunicationError,
    SmaInverterApiClientConnectionError,
    SmaInverterApiClientError,
)
from .const import (
    CONF_INVERTERS,
    CONF_INVERTER_HOST,
    CONF_INVERTER_NAME,
    CONF_INVERTER_PORT,
    CONF_INVERTER_SECTION,
    CONF_INVERTER_SLAVE_ID,
    CONF_SCAN_INTERVAL,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SLAVE_ID,
    DOMAIN,
    LOGGER,
)

# ---------------------------------------------------------------------------
# Step schemas
# ---------------------------------------------------------------------------

_GLOBAL_SCHEMA = vol.Schema(
    {
        vol.Optional(
            CONF_SCAN_INTERVAL,
            default=DEFAULT_SCAN_INTERVAL,
        ): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=10,
                max=3600,
                step=10,
                unit_of_measurement="s",
                mode=selector.NumberSelectorMode.BOX,
            )
        ),
    }
)

_INVERTER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_INVERTER_NAME): selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT),
        ),
        vol.Optional(CONF_INVERTER_SECTION, default=""): selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT),
        ),
        vol.Required(CONF_INVERTER_HOST): selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT),
        ),
        vol.Optional(
            CONF_INVERTER_PORT,
            default=DEFAULT_PORT,
        ): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=1,
                max=65535,
                step=1,
                mode=selector.NumberSelectorMode.BOX,
            )
        ),
        vol.Optional(
            CONF_INVERTER_SLAVE_ID,
            default=DEFAULT_SLAVE_ID,
        ): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=1,
                max=247,
                step=1,
                mode=selector.NumberSelectorMode.BOX,
            )
        ),
    }
)


class SmaInvertersConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SMA Inverters.

    Step 1 (``user``): global settings (scan interval).
    Step 2 (``inverter``): details for the first (or only) inverter,
        with live Modbus connection validation.
    """

    VERSION = 1

    def __init__(self) -> None:
        """Initialise the config flow."""
        self._data: dict[str, Any] = {CONF_INVERTERS: []}

    # ------------------------------------------------------------------
    # Step 1 – global settings
    # ------------------------------------------------------------------

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step (global settings)."""
        if user_input is not None:
            self._data[CONF_SCAN_INTERVAL] = int(user_input[CONF_SCAN_INTERVAL])
            return await self.async_step_inverter()

        return self.async_show_form(
            step_id="user",
            data_schema=_GLOBAL_SCHEMA,
        )

    # ------------------------------------------------------------------
    # Step 2 – first inverter details + connection test
    # ------------------------------------------------------------------

    async def async_step_inverter(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle inverter configuration step with Modbus connection test."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host: str = user_input[CONF_INVERTER_HOST].strip()
            port: int = int(user_input[CONF_INVERTER_PORT])
            slave_id: int = int(user_input[CONF_INVERTER_SLAVE_ID])

            try:
                await self._test_connection(host=host, port=port, slave_id=slave_id)
            except SmaInverterApiClientConnectionError as exc:
                LOGGER.warning("Connection test failed: %s", exc)
                errors["base"] = "connection"
            except SmaInverterApiClientCommunicationError as exc:
                LOGGER.error("Communication error during connection test: %s", exc)
                errors["base"] = "communication"
            except SmaInverterApiClientError as exc:
                LOGGER.exception("Unexpected error during connection test: %s", exc)
                errors["base"] = "unknown"
            else:
                inv_cfg: dict[str, Any] = {
                    CONF_INVERTER_NAME: user_input[CONF_INVERTER_NAME].strip(),
                    CONF_INVERTER_SECTION: user_input.get(
                        CONF_INVERTER_SECTION, ""
                    ).strip(),
                    CONF_INVERTER_HOST: host,
                    CONF_INVERTER_PORT: port,
                    CONF_INVERTER_SLAVE_ID: slave_id,
                }
                self._data[CONF_INVERTERS].append(inv_cfg)

                title = f"SMA Inverters – {host}"
                return self.async_create_entry(title=title, data=self._data)

        return self.async_show_form(
            step_id="inverter",
            data_schema=_INVERTER_SCHEMA,
            errors=errors,
        )

    # ------------------------------------------------------------------
    # Options flow
    # ------------------------------------------------------------------

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> SmaInvertersOptionsFlow:
        """Return the options flow handler."""
        return SmaInvertersOptionsFlow()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _test_connection(
        self,
        host: str,
        port: int,
        slave_id: int,
    ) -> None:
        """Open a Modbus TCP connection to verify the inverter is reachable."""
        client = SmaInverterApiClient(host=host, port=port, slave_id=slave_id)
        await client.async_test_connection()


class SmaInvertersOptionsFlow(config_entries.OptionsFlow):
    """Handle options for the SMA Inverters integration.

    Currently exposes the global scan interval so users can tune the
    poll frequency without re-adding the integration.
    """

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(
                data={CONF_SCAN_INTERVAL: int(user_input[CONF_SCAN_INTERVAL])}
            )

        current_interval: int = self.config_entry.data.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )

        options_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=current_interval,
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=10,
                        max=3600,
                        step=10,
                        unit_of_measurement="s",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
        )
