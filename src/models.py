from dataclasses import dataclass
from datetime import datetime

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
