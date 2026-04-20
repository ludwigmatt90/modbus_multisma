"""SMA Inverter Modbus API Client."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .const import (
    DEFAULT_PORT,
    DEFAULT_SLAVE_ID,
    MODBUS_TIMEOUT,
    REG_CURRENT_POWER,
    REG_TOTAL_ENERGY_START,
)


class SmaInverterApiClientError(Exception):
    """Exception to indicate a general API error."""


class SmaInverterApiClientCommunicationError(SmaInverterApiClientError):
    """Exception to indicate a communication error (e.g. host unreachable)."""


class SmaInverterApiClientConnectionError(SmaInverterApiClientCommunicationError):
    """Exception to indicate that the connection to the inverter failed."""


@dataclass
class InverterData:
    """Holds polled data for one inverter."""

    total_energy_kwh: float | None = None  # kWh
    current_power_w: float | None = None   # Watts


class SmaInverterApiClient:
    """Modbus TCP API client for a single SMA inverter."""

    def __init__(
        self,
        host: str,
        port: int = DEFAULT_PORT,
        slave_id: int = DEFAULT_SLAVE_ID,
    ) -> None:
        """Initialise the API client.

        Args:
            host: IP address or hostname of the inverter.
            port: Modbus TCP port (default 502).
            slave_id: Modbus unit/slave ID (SMA default is 3).

        """
        self._host = host
        self._port = port
        self._slave_id = slave_id

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    async def async_test_connection(self) -> bool:
        """Open a Modbus TCP connection and read a single register to verify
        reachability.  Returns *True* on success; raises on failure.
        """
        from pymodbus.client import AsyncModbusTcpClient  # noqa: PLC0415
        from pymodbus.exceptions import ModbusException  # noqa: PLC0415

        client = AsyncModbusTcpClient(
            host=self._host,
            port=self._port,
            timeout=MODBUS_TIMEOUT,
        )
        try:
            connected = await client.connect()
            if not connected:
                msg = f"Cannot connect to inverter at {self._host}:{self._port}"
                raise SmaInverterApiClientConnectionError(msg)
            # Read one register just to confirm Modbus responds correctly
            result = await client.read_input_registers(
                address=REG_TOTAL_ENERGY_START,
                count=2,
                slave=self._slave_id,
            )
            if result.isError():
                msg = f"Modbus error reading from {self._host}: {result}"
                raise SmaInverterApiClientCommunicationError(msg)
        except SmaInverterApiClientError:
            raise
        except ModbusException as exc:
            msg = f"Modbus protocol error for {self._host}: {exc}"
            raise SmaInverterApiClientCommunicationError(msg) from exc
        except OSError as exc:
            msg = f"Network error connecting to {self._host}:{self._port}: {exc}"
            raise SmaInverterApiClientConnectionError(msg) from exc
        finally:
            client.close()

        return True

    async def async_get_data(self) -> dict[str, Any]:
        """Poll the inverter and return a dict with the latest values.

        Keys match the sensor entity ``key`` values:
            * ``total_energy``  – total generated energy in kWh
            * ``current_power`` – current AC output power in W
        """
        from pymodbus.client import AsyncModbusTcpClient  # noqa: PLC0415
        from pymodbus.exceptions import ModbusException  # noqa: PLC0415

        client = AsyncModbusTcpClient(
            host=self._host,
            port=self._port,
            timeout=MODBUS_TIMEOUT,
        )
        try:
            connected = await client.connect()
            if not connected:
                msg = f"Cannot connect to inverter at {self._host}:{self._port}"
                raise SmaInverterApiClientConnectionError(msg)

            data: dict[str, Any] = {}

            # --- Total energy (2 x 16-bit registers → 32-bit unsigned, unit: Wh) ---
            result = await client.read_input_registers(
                address=REG_TOTAL_ENERGY_START,
                count=2,
                slave=self._slave_id,
            )
            if result.isError():
                msg = f"Modbus error reading total energy from {self._host}"
                raise SmaInverterApiClientCommunicationError(msg)

            raw_energy_wh = (result.registers[0] << 16) | result.registers[1]
            data["total_energy"] = raw_energy_wh / 1000.0  # Wh → kWh

            # --- Current AC power (2 x 16-bit registers → 32-bit signed, unit: W) ---
            result = await client.read_input_registers(
                address=REG_CURRENT_POWER,
                count=2,
                slave=self._slave_id,
            )
            if result.isError():
                msg = f"Modbus error reading current power from {self._host}"
                raise SmaInverterApiClientCommunicationError(msg)

            raw_power = (result.registers[0] << 16) | result.registers[1]
            # SMA encodes 0x80000000 as "not available"
            if raw_power == 0x80000000:
                data["current_power"] = None
            else:
                # Treat as signed 32-bit integer
                if raw_power >= 0x80000000:
                    raw_power -= 0x100000000
                data["current_power"] = float(raw_power)

        except SmaInverterApiClientError:
            raise
        except ModbusException as exc:
            msg = f"Modbus protocol error for {self._host}: {exc}"
            raise SmaInverterApiClientCommunicationError(msg) from exc
        except OSError as exc:
            msg = f"Network error communicating with {self._host}: {exc}"
            raise SmaInverterApiClientConnectionError(msg) from exc
        finally:
            client.close()

        return data
