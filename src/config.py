import json
import os
from pathlib import Path
from .models import Address


def load_addresses(config_path: str = "config/addresses.json") -> tuple[dict, list[Address]]:
    with open(config_path, "r") as f:
        data = json.load(f)

    global_config = data["global_config"]
    addresses = [
        Address(
            address=addr["address"].lower(),
            label=addr["label"],
            threshold_usdt=addr.get("threshold_usdt"),
        )
        for addr in data["addresses"]
    ]
    return global_config, addresses


def load_tagbook(tagbook_path: str = "config/tagbook.json") -> dict:
    with open(tagbook_path, "r") as f:
        data = json.load(f)
    # Normalizar claves a lowercase
    return {k.lower(): v for k, v in data.get("tags", {}).items()}


def get_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"Missing environment variable: {name}")
    return value
