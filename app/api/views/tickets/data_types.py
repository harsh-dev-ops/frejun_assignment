from dataclasses import dataclass


@dataclass
class CapacityCounts:
    total_confirmed: int
    total_rac: int
    total_waiting: int
    available_confirmed: int = 0
    available_rac: int = 0
    available_waiting: int = 0