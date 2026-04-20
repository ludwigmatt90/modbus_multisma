"""Custom types for the SMA Inverters integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

    from .coordinator import SmaInverterCoordinator


# Type alias: a ConfigEntry whose runtime_data is SmaInverterData
type SmaInverterConfigEntry = ConfigEntry[SmaInverterData]


@dataclass
class SmaInverterRuntimeData:
    """Runtime data stored per config-entry.

    Holds one coordinator per configured inverter. Each coordinator
    manages the polling lifecycle for a single Modbus device.
    """

    coordinators: list[SmaInverterCoordinator]
