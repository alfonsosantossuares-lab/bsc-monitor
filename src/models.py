from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Address:
    address: str
    label: str
    threshold_usdt: Optional[float] = None

    def effective_threshold(self, global_threshold: float) -> float:
        if self.threshold_usdt is not None:
            return self.threshold_usdt
        return global_threshold


@dataclass
class Movement:
    tx_hash: str
    block_number: int
    timestamp: datetime
    from_address: str
    to_address: str
    value_raw: str
    value_usdt: float
    contract: str
    direction: str
    monitored_address: str
    counterparty: str
    counterparty_label: Optional[str] = None


@dataclass
class DailyReport:
    date: str
    movements: list[Movement] = field(default_factory=list)
    alerts_triggered: list[Movement] = field(default_factory=list)

    def total_received(self) -> float:
        return sum(m.value_usdt for m in self.movements if m.direction == "in")

    def total_sent(self) -> float:
        return sum(m.value_usdt for m in self.movements if m.direction == "out")
