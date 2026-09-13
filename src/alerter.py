import requests
from .models import Movement


class TelegramAlerter:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    def send_alert(self, movement: Movement, threshold: float) -> bool:
        direction_emoji = "📥" if movement.direction == "in" else "📤"
        direction_text = "RECEPCION" if movement.direction == "in" else "ENVIO"

        counterparty_display = (
            movement.counterparty_label
            if movement.counterparty_label
            else f"{movement.counterparty[:10]}...{movement.counterparty[-6:]}"
        )

        message = (
            f"🚨 *Movimiento USDT Detectado*\n"
            f"\n"
            f"{direction_emoji} *{direction_text}*\n"
            f"📍 Cuenta: {movement.monitored_address[:10]}...{movement.monitored_address[-6:]}\n"
            f"🏷️ Label: {movement.counterparty_label or 'Sin etiqueta'}\n"
            f"💰 Monto: *{movement.value_usdt:,.2f} USDT*\n"
            f"👤 Contraparte: `{counterparty_display}`\n"
            f"⛓️ Tx: [Ver en Bscscan](https://bscscan.com/tx/{movement.tx_hash})\n"
            f"🧱 Bloque: {movement.block_number}\n"
            f"🕐 {movement.timestamp.strftime('%Y-%m-%d %H:%M UTC')}\n"
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
