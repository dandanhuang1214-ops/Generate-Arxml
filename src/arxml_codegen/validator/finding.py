"""Validation finding dataclass — models CORE-XXX findings like ARForge."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class Severity(Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass(slots=True)
class Finding:
    code: str             # e.g. CORE-010-DATAELEMENT-UNKNOWN-DATATYPE
    severity: Severity
    message: str
    location: str = ""    # e.g. "Ports!R12 InterfaceName"
    suggestion: str = ""

    def __str__(self):
        loc = f" [{self.location}]" if self.location else ""
        sug = f" — {self.suggestion}" if self.suggestion else ""
        return f"[{self.severity.value}] {self.code}{loc}: {self.message}{sug}"
