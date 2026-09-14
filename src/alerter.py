import requests
from .models import Movement

class TelegramAlerter:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    def send_alert(self, movement: Movement, threshold: float) -> bool:
        direction_emoji = "📥" if movement.direction == "in" else "📤"
        direction_text = "RECEPCIÓN" if movement.direction == "in" else "ENVÍO"
        
        # Determinar el rol de la contraparte
        role = "📤 Origen (Envió a tu wallet)" if movement.direction == "in" else "📥 Destino (Recibió de tu wallet)"
        
        # Formatear el saldo de la contraparte
        balance_str = f"{movement.counterparty_balance_usdt:,.2f} USDT" if movement.counterparty_balance_usdt > 0 else "0.00 USDT"

        message = (
            f"🚨 *Movimiento USDT Detectado*\n"
            f"\n"
            f"📍 *Tu Wallet:* {movement.monitored_label} (`{movement.monitored_address}`)\n"
            f"💰 *Monto:* {movement.value_usdt:,.2f} USDT\n"
            f"⏰ *Hora:* {movement.timestamp.strftime('%Y-%m-%d %H:%M UTC')}\n"
            f"\n"
            f"{role}:\n"
            f"🏷️ Dirección completa: `{movement.counterparty}`\n"
            f"💎 Saldo actual de esa dirección: *{balance_str}*\n"
            f"\n"
            f"🔗 *Transacción:* [Ver en Bscscan](https://bscscan.com/tx/{movement.tx_hash})\n"
            f"⚠️ Umbral superado: {threshold:,.0f} USDT"
        )

        try:
            resp = requests.post(
                f"{self.base_url}/sendMessage",
                json={
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": True,
                },
                timeout=15,
            )
            resp.raise_for_status()
            return True
        except Exception as e:
            print(f"Error sending alert: {e}")
            return False

    def send_daily_summary(self, total_in: float, total_out: float, count: int) -> bool:
        message = (
            f"📊 *Resumen Diario USDT*\n"
            f"\n"
            f"📥 Recibido: {total_in:,.2f} USDT\n"
            f"📤 Enviado: {total_out:,.2f} USDT\n"
            f"📈 Neto: {total_in - total_out:,.2f} USDT\n"
            f"🔢 Transacciones: {count}\n"
        )

        try:
            resp = requests.post(
                f"{self.base_url}/sendMessage",
                json={
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "Markdown",
                },
                timeout=15,
            )
            resp.raise_for_status()
            return True
        except Exception as e:
            print(f"Error sending summary: {e}")
            return False
