"""Sensor platform for SMA Inverters integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .inverter import Inverter

_LOGGER = logging.getLogger(__name__)

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


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SMA Inverter sensors from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    inverters: list[Inverter] = data["inverters"]

    entities: list[SmaInverterSensor] = []
    for inverter in inverters:
        for description in SENSOR_DESCRIPTIONS:
            entities.append(SmaInverterSensor(inverter, description, entry))

    async_add_entities(entities, update_before_add=True)


class SmaInverterSensor(SensorEntity):
    """Representation of an SMA Inverter sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        inverter: Inverter,
        description: SensorEntityDescription,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        self.entity_description = description
        self._inverter = inverter
        self._attr_unique_id = f"{inverter.key}_{description.key}"
        self._attr_native_value: float | None = None

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, inverter.key)},
            name=inverter.name,
            manufacturer="SMA",
            model="Solar Inverter",
            configuration_url=f"http://{inverter.ip}",
        )

    @property
    def available(self) -> bool:
        """Return True if the sensor is available."""
        return self._attr_native_value is not None

    async def async_update(self) -> None:
        """Fetch new state data for the sensor.

        This is where Modbus polling would occur in a full implementation.
        Currently returns None (unavailable) until inverter communication
        is implemented.
        """
        # Modbus polling placeholder — extend here with pymodbus reads
        # e.g. read REG_TOTAL_ENERGY_START for total_energy
        pass
