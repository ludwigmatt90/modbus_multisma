# SMA Inverters – Home Assistant Custom Integration

A Home Assistant custom integration that polls one or more **SMA solar inverters** via **Modbus TCP** and exposes their readings as sensor entities.

Built on the [integration_blueprint](https://github.com/ludeeus/integration_blueprint) template.

---

## Features

| Sensor | Unit | Description |
|--------|------|-------------|
| Total Energy | kWh | Cumulative energy generated (register 30529) |
| Current Power | W  | Instantaneous AC output power (register 30775) |

- **Per-inverter `DataUpdateCoordinator`** – each inverter is polled independently; one unreachable device does not affect the others.
- **UI-based config flow** – add inverters through the HA UI with live Modbus connection validation.
- **Options flow** – adjust the poll interval at any time without re-adding the integration.
- **HACS-compatible** – ready to install via the Home Assistant Community Store.

---

## Requirements

- Home Assistant 2024.1.0+
- Python library: `pymodbus >= 3.6.8` (installed automatically)
- SMA inverter with Modbus TCP enabled (typically port **502**, slave ID **3**)

---

## Installation

### Via HACS (recommended)

1. Open HACS → Integrations → ⋮ → **Custom repositories**.
2. Add this repository URL and select category **Integration**.
3. Search for *SMA Inverters* and install.
4. Restart Home Assistant.

### Manual

1. Copy the `custom_components/sma_inverters` folder into your `<config>/custom_components/` directory.
2. Restart Home Assistant.

---

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **SMA Inverters**.
3. **Step 1 – Global settings**: set the poll interval (default 30 s).
4. **Step 2 – Add inverter**: enter the inverter's name, IP address, Modbus port, and slave ID. The integration tests the connection before saving.

Additional inverters can be added by re-running the config flow or editing the integration options.

---

## Modbus Register Map

| Register | Count | Type | Scale | Meaning |
|----------|-------|------|-------|---------|
| 30529 | 2 | U32 | ÷ 1000 → kWh | Total energy produced (Wh raw) |
| 30775 | 2 | S32 | — | AC power output (W) |

> `0x80000000` is the SMA "not available" sentinel and is mapped to `None` (unavailable).

---

## Development

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate

# Install development dependencies
pip install homeassistant pymodbus ruff

# Lint
ruff check custom_components/sma_inverters/
ruff format --check custom_components/sma_inverters/
```

---

## Architecture

```
custom_components/sma_inverters/
├── __init__.py        # Integration setup / teardown
├── api.py             # SmaInverterApiClient (Modbus TCP)
├── config_flow.py     # UI config flow + options flow
├── const.py           # Constants, LOGGER, DOMAIN
├── coordinator.py     # SmaInverterCoordinator (DataUpdateCoordinator)
├── data.py            # Typed config-entry runtime data
├── entity.py          # SmaInverterEntity base class
├── sensor.py          # Sensor platform
├── manifest.json
└── translations/
    └── en.json
```

---

## Credits

- Template: [ludeeus/integration_blueprint](https://github.com/ludeeus/integration_blueprint)
- SMA Modbus documentation: [SMA Modbus Interface](https://www.sma.de/en/products/monitoring-control/modbus-protocol-inverters.html)
