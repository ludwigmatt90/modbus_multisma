"""Base entity class for SMA Inverters."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import SmaInverterCoordinator


class SmaInverterEntity(CoordinatorEntity[SmaInverterCoordinator]):
    """Base class for all SMA Inverter entities.

    Provides:
    * A :class:`DeviceInfo` that groups all entities for one physical
      inverter under a single device in the HA device registry.
    * The standard ``_attr_attribution`` populated from :data:`ATTRIBUTION`.
    * A unique-ID prefix derived from the inverter's coordinator name so
      that sensor/binary-sensor subclasses can append their own key.
    """

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SmaInverterCoordinator,
        inverter_key: str,
    ) -> None:
        """Initialise the base entity.

        Args:
            coordinator: The coordinator managing this inverter's data.
            inverter_key: A stable slug derived from the inverter's
                section + name, used as a sub-device identifier.

        """
        super().__init__(coordinator)
        self._inverter_key = inverter_key

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, inverter_key)},
            name=coordinator.inverter_name,
            manufacturer="SMA",
            model="Solar Inverter",
            # The web interface URL is inferred from the Modbus host
            configuration_url=f"http://{coordinator.client._host}",  # noqa: SLF001
        )
