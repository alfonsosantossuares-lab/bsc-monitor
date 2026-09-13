import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from .config import load_addresses, load_tagbook, get_env
from .bscscan_client import BscscanClient
from .alerter import TelegramAlerter
from .models import Movement


STATE_FILE = "state/last_block.json"


def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"last_block": 0, "addresses": {}}


def save_state(state: dict):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def parse_transfer(tx: dict, monitored_address: str, tagbook: dict) -> Movement:
    from_addr = tx["from"].lower()
    to_addr = tx["to"].lower()
    monitored = monitored_address.lower()
    decimals = int(tx.get("tokenDecimal", 18))
    value_raw = tx["value"]
    value_usdt = int(value_raw) / (10 ** decimals)

    direction = "in" if to_addr == monitored else "out"
    counterparty = from_addr if direction == "in" else to_addr
    counterparty_label = tagbook.get(counterparty, {}).get("label")

    return Movement(
        tx_hash=tx["hash"],
        block_number=int(tx["blockNumber"]),
        timestamp=datetime.fromtimestamp(int(tx["timeStamp"]), tz=timezone.utc),
        from_address=from_addr,
        to_address=to_addr,
        value_raw=value_raw,
        value_usdt=value_usdt,
        contract=tx.get("contractAddress", "").lower(),
        direction=direction,
        monitored_address=monitored,
        counterparty=counterparty,
        counterparty_label=counterparty_label,
    )


def run():
    print(f"[{datetime.now(timezone.utc)}] Starting poll...")

    # Cargar config
    global_config, addresses = load_addresses()
    tagbook = load_tagbook()
    state = load_state()

    # Inicializar clientes
    client = BscscanClient(api_key=get_env("BSCSCAN_API_KEY"))
    alerter = TelegramAlerter(
        bot_token=get_env("TELEGRAM_BOT_TOKEN"),
        chat_id=get_env("TELEGRAM_CHAT_ID"),
    )

    # Obtener ultimo bloque de la red
    latest_block = client.get_latest_block()
    print(f"Latest BSC block: {latest_block}")

    all_movements = []

    for addr in addresses:
        addr_lower = addr.address.lower()
        last_block = state.get("addresses", {}).get(addr_lower, 0)

        # Si es la primera vez, empezar desde 5000 bloques atras (~4 horas)
        if last_block == 0:
            last_block = latest_block - 5000
            print(f"  [{addr.label}] First run, starting from block {last_block}")
        else:
            last_block += 1  # No repetir el ultimo bloque procesado

        if last_block > latest_block:
            print(f"  [{addr.label}] No new blocks to process")
            continue

        print(f"  [{addr.label}] Scanning blocks {last_block} to {latest_block}...")

        try:
            transfers = client.get_usdt_transfers(addr_lower, last_block)
        except Exception as e:
            print(f"  [{addr.label}] Error fetching transfers: {e}")
            continue

        print(f"  [{addr.label}] Found {len(transfers)} USDT transfers")

        threshold = addr.effective_threshold(global_config["default_threshold_usdt"])

        for tx in transfers:
            movement = parse_transfer(tx, addr_lower, tagbook)
            all_movements.append(movement)

            if movement.value_usdt >= threshold:
                print(f"    🚨 ALERT: {movement.direction} {movement.value_usdt:,.2f} USDT")
                alerter.send_alert(movement, threshold)

        # Actualizar estado
        if "addresses" not in state:
            state["addresses"] = {}
        state["addresses"][addr_lower] = latest_block

    state["last_block"] = latest_block
    save_state(state)

    print(f"[{datetime.now(timezone.utc)}] Poll complete. {len(all_movements)} total movements.")

    # Guardar movimientos del dia para el reporte
    if all_movements:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        daily_file = f"state/daily_{today}.json"
        existing = []
        if os.path.exists(daily_file):
            with open(daily_file, "r") as f:
                existing = json.load(f)

        new_entries = [
            {
                "tx_hash": m.tx_hash,
                "block_number": m.block_number,
                "timestamp": m.timestamp.isoformat(),
                "from": m.from_address,
                "to": m.to_address,
                "value_usdt": m.value_usdt,
                "direction": m.direction,
                "monitored": m.monitored_address,
                "counterparty": m.counterparty,
                "counterparty_label": m.counterparty_label,
            }
            for m in all_movements
        ]
        existing.extend(new_entries)

        with open(daily_file, "w") as f:
            json.dump(existing, f, indent=2)

    return all_movements


if __name__ == "__main__":
    run()
