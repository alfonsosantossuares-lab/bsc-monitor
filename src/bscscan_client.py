import time
import requests


class BscscanClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Actualizado a API V2 de Bscscan
        self.base_url = "https://api.bscscan.com/v2/api"
        self._last_call = 0.0
        self._min_interval = 0.25  # 4 calls/seg (margen sobre limite de 5)

    def _rate_limit(self):
        elapsed = time.time() - self._last_call
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_call = time.time()

    def _get(self, params: dict) -> dict:
        self._rate_limit()
        params["apikey"] = self.api_key
        # chainid 56 es obligatorio para la API V2 de Bscscan
        params["chainid"] = "56"
        
        resp = requests.get(self.base_url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        
        if data.get("status") == "0" and data.get("message") != "No transactions found":
            raise RuntimeError(f"Bscscan error: {data.get('message')} - {data.get('result')}")
        return data

    def get_usdt_transfers(self, address: str, start_block: int) -> list[dict]:
        params = {
            "module": "account",
            "action": "tokentx",
            "contractaddress": "0x55d398326f99059fF7754852469990354080808a",
            "address": address,
            "startblock": start_block,
            "endblock": 99999999,
            "sort": "asc",
        }
        data = self._get(params)
        result = data.get("result", [])
        if isinstance(result, str):
            return []
        return result

    def get_latest_block(self) -> int:
        params = {"module": "proxy", "action": "eth_blockNumber"}
        data = self._get(params)
        return int(data["result"], 16)
