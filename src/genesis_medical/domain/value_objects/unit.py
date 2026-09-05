from dataclasses import dataclass

@dataclass(frozen=True)
class Unit:
    name: str