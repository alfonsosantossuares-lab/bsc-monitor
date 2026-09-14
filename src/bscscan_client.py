import requests

class BscscanClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.bscscan.com/api"
        self.usdt_contract = "0x55d398326f99059fF7754852469990354080808a"

    def get_latest_block(self) -> int:
        url = f"{self.base_url}?module=proxy&action=eth_blockNumber&apikey={self.api_key}"
        resp = requests.get(url, timeout=10)
        return int(resp.json()["result"], 16)

    def get_usdt_transfers(self, address: str, start_block: int) -> list:
        url = f"{self.base_url}?module=account&action=tokentx&contractaddress={self.usdt_contract}&address={address}&startblock={start_block}&sort=asc&apikey={self.api_key}"
        resp = requests.get(url, timeout=15)
        data = resp.json()
        return data.get("result", []) if data.get("status") == "1" else []

    # 🌟 NUEVO MÉTODO: Obtiene el saldo USDT de una dirección
    def get_usdt_balance(self, address: str) -> float:
        url = f"{self.base_url}?module=account&action=tokenbalance&contractaddress={self.usdt_contract}&address={address}&tag=latest&apikey={self.api_key}"
        try:
            resp = requests.get(url, timeout=10)
            data = resp.json()
            if data.get("status") == "1":
                return int(data["result"]) / 1e18
            return 0.0
        except Exception:
            return 0.0
