import base64
import hashlib
import hmac
from typing import Any, Protocol

from app.core.config import settings


def verify_midtrans_signature(
    order_id: str,
    status_code: str,
    gross_amount: str,
    signature_key: str,
    server_key: str | None = None,
) -> bool:
    """Verifies Midtrans notification signature key using constant-time comparison.

    Rule: SHA512(order_id + status_code + gross_amount + server_key)
    """
    key = server_key or settings.MIDTRANS_SERVER_KEY
    if not key:
        return False

    raw_signature_input = f"{order_id}{status_code}{gross_amount}{key}"
    expected_hash = hashlib.sha512(
        raw_signature_input.encode("utf-8")).hexdigest()
    return hmac.compare_digest(expected_hash, signature_key.lower())


class PaymentGateway(Protocol):
    """Port interface for third-party payment gateway integration."""

    async def create_snap_transaction(
        self,
        order_id: str,
        gross_amount: int,
        customer_name: str,
        customer_email: str | None,
    ) -> dict[str, str]:
        """Creates payment transaction and returns {'token': '...', 'redirect_url': '...'}."""
        ...

    async def get_transaction_status(self, order_id: str) -> dict[str, Any]:
        """Queries transaction status directly from the gateway."""
        ...


class MidtransGateway:
    """Real adapter for Midtrans Snap API (Sandbox & Production)."""

    def __init__(self) -> None:
        self.is_production = settings.MIDTRANS_IS_PRODUCTION
        self.server_key = settings.MIDTRANS_SERVER_KEY
        self.base_url = (
            "https://app.midtrans.com/snap/v1"
            if self.is_production
            else "https://app.sandbox.midtrans.com/snap/v1"
        )
        self.api_url = (
            "https://api.midtrans.com/v2"
            if self.is_production
            else "https://api.sandbox.midtrans.com/v2"
        )

    def _get_headers(self) -> dict[str, str]:
        auth_string = f"{self.server_key}:"
        encoded = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Basic {encoded}",
        }

    async def create_snap_transaction(
        self,
        order_id: str,
        gross_amount: int,
        customer_name: str,
        customer_email: str | None,
    ) -> dict[str, str]:
        import httpx

        url = f"{self.base_url}/transactions"
        payload = {
            "transaction_details": {
                "order_id": order_id,
                "gross_amount": gross_amount,
            },
            "customer_details": {
                "first_name": customer_name,
                "email": customer_email or "billing@pelanggan.local",
            },
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload, headers=self._get_headers())
            resp.raise_for_status()
            data = resp.json()
            return {
                "token": data.get("token", ""),
                "redirect_url": data.get("redirect_url", ""),
            }

    async def get_transaction_status(self, order_id: str) -> dict[str, Any]:
        import httpx

        url = f"{self.api_url}/{order_id}/status"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers=self._get_headers())
            resp.raise_for_status()
            return resp.json()


class FakePaymentGateway:
    """Fake adapter for development, CI, and local tests without API keys."""

    async def create_snap_transaction(
        self,
        order_id: str,
        gross_amount: int,
        customer_name: str,
        customer_email: str | None,
    ) -> dict[str, str]:
        return {
            "token": f"fake-snap-token-{order_id}",
            "redirect_url": f"https://app.sandbox.midtrans.com/snap/v2/vtweb/fake-{order_id}",
        }

    async def get_transaction_status(self, order_id: str) -> dict[str, Any]:
        return {
            "order_id": order_id,
            "transaction_status": "settlement",
            "fraud_status": "accept",
            "status_code": "200",
            "gross_amount": "100000",
        }


def get_payment_gateway() -> PaymentGateway:
    """Factory returning configured payment gateway adapter."""
    if settings.MIDTRANS_SERVER_KEY:
        return MidtransGateway()
    return FakePaymentGateway()
