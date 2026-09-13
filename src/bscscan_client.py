import time
import requests


class BscscanClient:
    def __init__(self, api_key: str = ""):
        # Usamos el nodo RPC público oficial de BSC. 
        # No requiere API key, no tiene costo y es 100% fiable.
        self.rpc_url = "https://bsc-dataseed.binance.org/"
        self._last_call = 0.0
        self._min_interval = 0.1  # 10 llamadas por segundo (muy seguro)

    def _rate_limit(self):
        elapsed = time.time() - self._last_call
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_call = time.time()

    def _rpc_call(self, method: str, params: list) -> dict:
        self._rate_limit()
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        resp = requests.post(self.rpc_url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            raise RuntimeError(f"RPC Error: {data['error']}")
        return data["result"]

    def get_latest_block(self) -> int:
        result = self._rpc_call("eth_blockNumber", [])
        return int(result, 16)

    def get_usdt_transfers(self, address: str, start_block: int) -> list[dict]:
        contract = "0x55d398326f99059fF7754852469990354080808a"
        # Topic 0 del evento Transfer de ERC-20/BEP-20
        topic0 = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
        
        transfers = []
        current_start = start_block
        latest_block = self.get_latest_block()
        chunk_size = 2000  # Límite seguro para nodos públicos
        
        while current_start <= latest_block:
            current_end = min(current_start + chunk_size - 1, latest_block)
            
            logs = self._rpc_call("eth_getLogs", [{
                "address": contract,
                "fromBlock": hex(current_start),
                "toBlock": hex(current_end)
            }])
            
            for log in logs:
                # Los temas 1 y 2 son las direcciones 'from' y 'to' (con relleno de ceros)
                from_addr = "0x" + log["topics"][1][26:].lower()
                to_addr = "0x" + log["topics"][2][26:].lower()
                
                if from_addr == address.lower() or to_addr == address.lower():
                    # Obtener la marca de tiempo del bloque
                    block_num = hex(log["blockNumber"])
                    block_data = self._rpc_call("eth_getBlockByNumber", [block_num, False])
                    timestamp = int(block_data["timestamp"], 16)
                    
                    value_int = int(log["data"], 16)
                    
                    transfers.append({
                        "hash": log["transactionHash"],
                        "blockNumber": int(log["blockNumber"], 16),
                        "timeStamp": str(timestamp),
                        "from": from_addr,
                        "to": to_addr,
                        "value": str(value_int),
                        "tokenDecimal": "18",
                        "contractAddress": contract
                    })
            
            current_start = current_end + 1
            
        return transfers
