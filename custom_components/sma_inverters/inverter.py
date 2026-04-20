"""Inverter model definitions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Inverter:
    """SMA inverter runtime model."""

    name: str
    section: str
    ip: str

    @property
    def key(self) -> str:
        safe_section = self.section.strip().lower().replace(" ", "_")
        safe_name = self.name.strip().lower().replace(" ", "_")
        return f"{safe_section}_{safe_name}"
