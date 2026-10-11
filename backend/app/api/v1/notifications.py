from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.deps import require_permission
from app.integrations.notifications import get_telegram_notifier
from app.models.user import User

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class TestTelegramRequest(BaseModel):
    message: str = "Pesan uji coba koneksi bot Telegram Lumbung ERP."
    chat_id: str | None = None


@router.post("/test-telegram")
async def test_telegram_connection(
    req: TestTelegramRequest,
    current_user: User = Depends(require_permission("manage", "system")),
):
    notifier = get_telegram_notifier()
    success = await notifier.send_message(text=req.message, chat_id=req.chat_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"code": "TELEGRAM_GAGAL",
                    "message": "Gagal mengirim pesan melalui Telegram Bot API. Periksa token dan chat ID."},
        )
    return {"status": "success", "message": "Pesan Telegram berhasil dikirim atau dicatat"}
