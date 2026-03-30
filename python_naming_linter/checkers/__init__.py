from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Violation:
    rule_name: str
    file_path: str
    lineno: int
    name: str
    message: str
