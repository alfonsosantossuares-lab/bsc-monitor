import requests

class BscscanClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Usamos la API V2 de Etherscan/Bscscan
        self.base_url = "https://api.etherscan.io/v2/api"
        self.usdt_contract = "0x55d398326f99059fF7754852469990354080808a"
        self.rpc_url = "https://bsc-dataseed.binance.org/"

    def get_latest_block(self) -> int:
        # Usamos RPC público para obtener el último bloque (evita el error de API V1)
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_blockNumber",
            "params": [],
            "id": 1
        }
        try:
            resp = requests.post(self.rpc_url, json=payload, timeout=10)
            resp.raise_for_status()
            return int(resp.json()["result"], 16)
        except Exception:
            # Fallback a API V2 si el RPC falla
            url = f"{self.base_url}?chainid=56&module=proxy&action=eth_blockNumber&apikey={self.api_key}"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            if data.get("status") == "1":
                return int(data["result"], 16)
            raise Exception(f"Failed to get latest block: {data}")

    def get_usdt_transfers(self, address: str, start_block: int) -> list:
        # API V2 requiere chainid=56
        url = f"{self.base_url}?chainid=56&module=account&action=tokentx&contractaddress={self.usdt_contract}&address={address}&startblock={start_block}&sort=asc&apikey={self.api_key}"
        resp = requests.get(url, timeout=15)
        data = resp.json()
        return data.get("result", []) if data.get("status") == "1" else []

    def get_usdt_balance(self, address: str) -> float:
        # API V2 requiere chainid=56
        url = f"{self.base_url}?chainid=56&module=account&action=tokenbalance&contractaddress={self.usdt_contract}&address={address}&tag=latest&apikey={self.api_key}"
        try:
            resp = requests.get(url, timeout=10)
            data = resp.json()
            if data.get("status") == "1":
                return int(data["result"]) / 1e18
            return 0.0
        except Exception:
            return 0.0
