import logging
from typing import Protocol

from app.core.config import settings

logger = logging.getLogger(__name__)


class TelegramNotifier(Protocol):
    """Port interface for Telegram alert notifications."""

    async def send_message(self, text: str, chat_id: str | None = None) -> bool:
        ...

    async def notify_low_stock(
        self, product_name: str, sku: str, on_hand: int, min_stock: int
    ) -> bool:
        ...

    async def notify_payment_received(
        self, invoice_number: str, amount: int, method: str, customer_name: str
    ) -> bool:
        ...

    async def notify_invoice_overdue(
        self, invoice_number: str, customer_name: str, total: int, due_date: str
    ) -> bool:
        ...


class RealTelegramNotifier:
    """Driven adapter sending notifications to Telegram Bot API."""

    def __init__(self, bot_token: str, default_chat_id: str) -> None:
        self.bot_token = bot_token
        self.default_chat_id = default_chat_id
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    async def send_message(self, text: str, chat_id: str | None = None) -> bool:
        target_chat = chat_id or self.default_chat_id
        if not self.bot_token or not target_chat:
            logger.warning("Telegram Bot Token atau Chat ID belum disetel")
            return False

        import httpx

        payload = {
            "chat_id": target_chat,
            "text": text,
            "parse_mode": "Markdown",
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(self.api_url, json=payload)
                res.raise_for_status()
                return True
        except Exception as e:
            logger.error("Gagal mengirim notifikasi Telegram: %s", e)
            return False

    async def notify_low_stock(
        self, product_name: str, sku: str, on_hand: int, min_stock: int
    ) -> bool:
        msg = (
            "🚨 *PERINGATAN STOK MENIPIS*\n\n"
            f"*Produk:* {product_name} (`{sku}`)\n"
            f"*Stok Tersedia:* `{on_hand}` unit\n"
            f"*Batas Minimum:* `{min_stock}` unit\n"
            "_Segera buat Purchase Order (PO) ke pemasok._"
        )
        return await self.send_message(msg)

    async def notify_payment_received(
        self, invoice_number: str, amount: int, method: str, customer_name: str
    ) -> bool:
        msg = (
            "💰 *PEMBAYARAN DITERIMA*\n\n"
            f"*No Faktur:* `{invoice_number}`\n"
            f"*Pelanggan:* {customer_name}\n"
            f"*Nominal:* *Rp {amount:,}*\n"
            f"*Metode:* `{method.upper()}`\n"
            "_Status faktur telah diperbarui di sistem Lumbung._"
        )
        return await self.send_message(msg)

    async def notify_invoice_overdue(
        self, invoice_number: str, customer_name: str, total: int, due_date: str
    ) -> bool:
        msg = (
            "⚠️ *FAKTUR JATUH TEMPO*\n\n"
            f"*No Faktur:* `{invoice_number}`\n"
            f"*Pelanggan:* {customer_name}\n"
            f"*Total Tagihan:* *Rp {total:,}*\n"
            f"*Jatuh Tempo:* `{due_date}`\n"
            "_Mohon tim penagihan menghubungi pelanggan bersangkutan._"
        )
        return await self.send_message(msg)


class FakeTelegramNotifier:
    """In-memory mock notifier for development, tests, and CI."""

    def __init__(self) -> None:
        self.sent_messages: list[str] = []

    async def send_message(self, text: str, chat_id: str | None = None) -> bool:
        self.sent_messages.append(text)
        logger.info("[MOCK TELEGRAM] to %s:\n%s", chat_id, text)
        return True

    async def notify_low_stock(
        self, product_name: str, sku: str, on_hand: int, min_stock: int
    ) -> bool:
        msg = f"[LOW STOCK ALERT] {product_name} ({sku}) on_hand: {on_hand}/{min_stock}"
        self.sent_messages.append(msg)
        return True

    async def notify_payment_received(
        self, invoice_number: str, amount: int, method: str, customer_name: str
    ) -> bool:
        msg = f"[PAYMENT ALERT] {invoice_number} Rp {amount:,} from {customer_name}"
        self.sent_messages.append(msg)
        return True

    async def notify_invoice_overdue(
        self, invoice_number: str, customer_name: str, total: int, due_date: str
    ) -> bool:
        msg = f"[OVERDUE ALERT] {invoice_number} Rp {total:,} due: {due_date}"
        self.sent_messages.append(msg)
        return True


def get_telegram_notifier() -> TelegramNotifier:
    """Factory returning configured Telegram notification adapter."""
    if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID:
        return RealTelegramNotifier(
            bot_token=settings.TELEGRAM_BOT_TOKEN,
            default_chat_id=settings.TELEGRAM_CHAT_ID,
        )
    return FakeTelegramNotifier()
