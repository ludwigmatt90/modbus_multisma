"""DataUpdateCoordinator for the SMA Inverters integration."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    SmaInverterApiClient,
    SmaInverterApiClientCommunicationError,
    SmaInverterApiClientError,
)
from .const import DOMAIN, LOGGER

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


class SmaInverterCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator that polls a single SMA inverter via Modbus TCP.

    One coordinator instance is created per inverter entry in the
    config.  ``coordinator.data`` is a plain dict with keys matching
    the sensor entity ``key`` values (e.g. ``"total_energy"``,
    ``"current_power"``).
    """

    def __init__(
        self,
        hass: HomeAssistant,
        client: SmaInverterApiClient,
        inverter_name: str,
        scan_interval: int,
    ) -> None:
        """Initialise the coordinator.

        Args:
            hass: The Home Assistant instance.
            client: A configured :class:`SmaInverterApiClient`.
            inverter_name: Human-readable name used in log messages.
            scan_interval: Poll interval in seconds.

        """
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=f"{DOMAIN}_{inverter_name}",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client
        self.inverter_name = inverter_name

    # ------------------------------------------------------------------
    # DataUpdateCoordinator protocol
    # ------------------------------------------------------------------

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch the latest data from the inverter.

        Called automatically by the coordinator framework.  Raises
        :class:`UpdateFailed` so HA marks all entities as unavailable
        when the inverter cannot be reached.
        """
        try:
            return await self.client.async_get_data()
        except SmaInverterApiClientCommunicationError as exc:
            msg = (
                f"Communication error while polling inverter "
                f"'{self.inverter_name}': {exc}"
            )
            raise UpdateFailed(msg) from exc
        except SmaInverterApiClientError as exc:
            msg = f"Unexpected error from inverter '{self.inverter_name}': {exc}"
            raise UpdateFailed(msg) from exc
