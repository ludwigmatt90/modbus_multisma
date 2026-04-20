"""Sensor platform for the SMA Inverters integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfEnergy, UnitOfPower

from .entity import SmaInverterEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import SmaInverterCoordinator
    from .data import SmaInverterConfigEntry

# ---------------------------------------------------------------------------
# Sensor descriptions
# ---------------------------------------------------------------------------

SENSOR_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="total_energy",
        name="Total Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:solar-power",
    ),
    SensorEntityDescription(
        key="current_power",
        name="Current Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash",
    ),
)


# ---------------------------------------------------------------------------
# Platform setup
# ---------------------------------------------------------------------------


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001
    entry: SmaInverterConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SMA Inverter sensor entities from a config entry.

    One :class:`SmaInverterSensor` is created per (inverter × description)
    combination.  Each inverter has its own coordinator so that a single
    failing device does not affect the others.
    """
    entities: list[SmaInverterSensor] = [
        SmaInverterSensor(
            coordinator=coordinator,
            entity_description=description,
        )
        for coordinator in entry.runtime_data.coordinators
        for description in SENSOR_DESCRIPTIONS
    ]

    async_add_entities(entities)


# ---------------------------------------------------------------------------
# Sensor entity
# ---------------------------------------------------------------------------


class SmaInverterSensor(SmaInverterEntity, SensorEntity):
    """Sensor entity for a single measurement on one SMA inverter.

    Data is provided by the coordinator; when the coordinator cannot reach
    the inverter, ``available`` is automatically ``False`` and HA marks
    the entity as unavailable.
    """

    def __init__(
        self,
        coordinator: SmaInverterCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialise the sensor.

        Args:
            coordinator: The coordinator that polls this inverter.
            entity_description: Describes the measurement (key, unit, …).

        """
        # Derive a stable slug from the coordinator name (= inverter name)
        inverter_key = coordinator.name.removeprefix(f"{coordinator.name.split('_')[0]}_")

        super().__init__(coordinator=coordinator, inverter_key=inverter_key)

        self.entity_description = entity_description

        # Unique ID = <inverter_key>_<sensor_key> so it survives renames
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}"
            f"_{coordinator.inverter_name.lower().replace(' ', '_')}"
            f"_{entity_description.key}"
        )

    # ------------------------------------------------------------------
    # SensorEntity protocol
    # ------------------------------------------------------------------

    @property
    def native_value(self) -> float | None:
        """Return the current sensor value from coordinator data."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self.entity_description.key)
