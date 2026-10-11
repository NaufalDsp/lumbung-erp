from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from app.core.config import settings

# --- Password Hashing (Argon2id with standard-library fallback) ---
try:
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError
    _hasher = PasswordHasher(time_cost=2, memory_cost=19456, parallelism=1)

    def hash_password(password: str) -> str:
        return _hasher.hash(password)

    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            return _hasher.verify(hashed_password, plain_password)
        except (VerifyMismatchError, Exception):
            return False

except ImportError:
    # Standard-library PBKDF2-HMAC-SHA256 fallback when argon2-cffi is not yet installed
    def hash_password(password: str) -> str:
        salt = secrets.token_bytes(16)
        key = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, 100_000)
        return f"pbkdf2:sha256:100000${salt.hex()}${key.hex()}"

    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            if not hashed_password.startswith("pbkdf2:sha256:"):
                return False
            parts = hashed_password.split("$")
            salt = bytes.fromhex(parts[1])
            expected_key = bytes.fromhex(parts[2])
            key = hashlib.pbkdf2_hmac(
                "sha256", plain_password.encode("utf-8"), salt, 100_000)
            return hmac.compare_digest(key, expected_key)
        except Exception:
            return False


# --- Token Management (PyJWT with HMAC-SHA256 fallback) ---
try:
    import jwt
    _JWT_AVAILABLE = True
except ImportError:
    _JWT_AVAILABLE = False


def _b64_url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64_url_decode(s: str) -> bytes:
    padding = "=" * (4 - (len(s) % 4))
    return base64.urlsafe_b64decode(s + padding)


def create_access_token(
    subject: str | int,
    claims: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token valid for 15 minutes by default."""
    now = datetime.now(timezone.utc)
    delta = expires_delta or timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = now + delta

    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    if claims:
        payload.update(claims)

    if _JWT_AVAILABLE:
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    # Pure Python fallback for environments without PyJWT
    header = {"alg": "HS256", "typ": "JWT"}
    header_bytes = _b64_url_encode(json.dumps(
        header, separators=(",", ":")).encode("utf-8"))
    payload_bytes = _b64_url_encode(json.dumps(
        payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_bytes}.{payload_bytes}"
    signature = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        signing_input.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return f"{signing_input}.{_b64_url_encode(signature)}"


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and verify signature and expiration of JWT access token."""
    if _JWT_AVAILABLE:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"],
            options={"require": ["sub", "exp"]},
        )

    # Pure Python verification fallback
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid JWT token format")

    header_b64, payload_b64, signature_b64 = parts
    signing_input = f"{header_b64}.{payload_b64}"
    expected_sig = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        signing_input.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    sig = _b64_url_decode(signature_b64)
    if not hmac.compare_digest(sig, expected_sig):
        raise ValueError("Signature mismatch")

    payload: dict[str, Any] = json.loads(
        _b64_url_decode(payload_b64).decode("utf-8"))
    exp = payload.get("exp")
    if exp is not None and datetime.now(timezone.utc).timestamp() > exp:
        raise ValueError("Token expired")

    return payload


def hash_token(raw_token: str) -> str:
    """Generate SHA-256 hash of a raw token for safe persistence."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def generate_refresh_token() -> tuple[str, str]:
    """Generate a high-entropy 256-bit random refresh token and its SHA-256 hash."""
    raw_token = secrets.token_urlsafe(32)
    token_hash = hash_token(raw_token)
    return raw_token, token_hash
