from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Address:
    address: str
    label: str
    threshold_usdt: Optional[float] = None

    def effective_threshold(self, default: float) -> float:
        """Devuelve el umbral específico de esta dirección, o el global si no tiene."""
        return self.threshold_usdt if self.threshold_usdt is not None else default


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
    monitored_label: str               # <-- NUEVO: Para mostrar "K", "G", etc.
    counterparty: str
    counterparty_label: str
    counterparty_balance_usdt: float = 0.0  # <-- NUEVO: Saldo de la contraparte
