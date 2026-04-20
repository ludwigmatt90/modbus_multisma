"""SMA Inverters integration for Home Assistant.

Polls one or more SMA solar inverters via Modbus TCP and exposes their
readings as Home Assistant sensor entities.

For more details about this integration, please refer to
https://github.com/example/sma_inverters
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import Platform

from .api import SmaInverterApiClient
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
from .coordinator import SmaInverterCoordinator
from .data import SmaInverterRuntimeData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import SmaInverterConfigEntry

PLATFORMS: list[Platform] = [Platform.SENSOR]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: SmaInverterConfigEntry,
) -> bool:
    """Set up SMA Inverters from a config entry."""
    scan_interval: int = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    inverters_config: list[dict] = entry.data.get(CONF_INVERTERS, [])

    coordinators: list[SmaInverterCoordinator] = []

    for inv_cfg in inverters_config:
        section: str = inv_cfg.get(CONF_INVERTER_SECTION, "")
        name: str = inv_cfg.get(CONF_INVERTER_NAME, "inverter")
        host: str = inv_cfg[CONF_INVERTER_HOST]
        port: int = inv_cfg.get(CONF_INVERTER_PORT, DEFAULT_PORT)
        slave_id: int = inv_cfg.get(CONF_INVERTER_SLAVE_ID, DEFAULT_SLAVE_ID)

        # Build a stable slug used as the device identifier
        safe_section = section.strip().lower().replace(" ", "_")
        safe_name = name.strip().lower().replace(" ", "_")
        inverter_key = f"{safe_section}_{safe_name}" if safe_section else safe_name

        client = SmaInverterApiClient(
            host=host,
            port=port,
            slave_id=slave_id,
        )

        coordinator = SmaInverterCoordinator(
            hass=hass,
            client=client,
            inverter_name=name,
            scan_interval=scan_interval,
        )

        # Perform the first data fetch; raises ConfigEntryNotReady on failure
        # so HA will retry the setup automatically.
        await coordinator.async_config_entry_first_refresh()

        coordinators.append(coordinator)

    entry.runtime_data = SmaInverterRuntimeData(coordinators=coordinators)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Reload the entry when the user updates its options
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: SmaInverterConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: SmaInverterConfigEntry,
) -> None:
    """Reload the config entry when options are updated."""
    LOGGER.debug("Reloading SMA Inverters entry %s", entry.entry_id)
    await hass.config_entries.async_reload(entry.entry_id)
