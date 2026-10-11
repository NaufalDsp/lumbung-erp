from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.permissions import Permission, has_permission
from app.core.security import decode_access_token
from app.domain.enums import UserRole
from app.models.database import get_db
from app.models.user import User

security_scheme = HTTPBearer(auto_error=False)

# Fixed Demo Persona Profiles for instant login (PRD Section 11 F1)
DEMO_PERSONAS: dict[str, dict[str, str | int | bool]] = {
    "admin": {
        "id": 1,
        "email": "admin@lumbung.local",
        "name": "Budi Santoso (Admin)",
        "role": UserRole.ADMIN.value,
        "is_active": True,
    },
    "sales": {
        "id": 2,
        "email": "sales@lumbung.local",
        "name": "Rina Wijaya (Penjualan)",
        "role": UserRole.SALES.value,
        "is_active": True,
    },
    "warehouse": {
        "id": 3,
        "email": "warehouse@lumbung.local",
        "name": "Joko Susilo (Gudang)",
        "role": UserRole.WAREHOUSE.value,
        "is_active": True,
    },
    "finance": {
        "id": 4,
        "email": "finance@lumbung.local",
        "name": "Siti Rahma (Keuangan)",
        "role": UserRole.FINANCE.value,
        "is_active": True,
    },
}


class AuthenticatedUser:
    """Lightweight user model representation for authenticated contexts."""

    def __init__(self, id: int, email: str, name: str, role: str, is_active: bool) -> None:
        self.id = id
        self.email = email
        self.name = name
        self.role = role
        self.is_active = is_active


async def get_current_user(
    token_auth: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AuthenticatedUser:
    if not token_auth or not token_auth.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "TIDAK_TEROTENTIKASI",
                              "message": "Token akses tidak disertakan"}},
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(token_auth.credentials)
        user_id_str: str | None = payload.get("sub")
        if not user_id_str:
            raise ValueError("Token does not contain 'sub'")
        user_id = int(user_id_str)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "TOKEN_TIDAK_VALID",
                              "message": "Token akses kadaluwarsa atau tidak valid"}},
            headers={"WWW-Authenticate": "Bearer"},
        )

    # In DEMO_MODE, support demo persona tokens directly
    demo_role = payload.get("role")
    if settings.DEMO_MODE and demo_role in DEMO_PERSONAS and user_id in (1, 2, 3, 4):
        persona = DEMO_PERSONAS[demo_role]
        return AuthenticatedUser(
            id=int(persona["id"]),
            email=str(persona["email"]),
            name=str(persona["name"]),
            role=str(persona["role"]),
            is_active=bool(persona["is_active"]),
        )

    # Query DB for persistent users
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "PENGGUNA_TIDAK_DITEMUKAN",
                              "message": "Pengguna tidak terdaftar"}},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "PENGGUNA_NONAKTIF",
                              "message": "Akun pengguna dinonaktifkan"}},
        )

    return AuthenticatedUser(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        is_active=user.is_active,
    )


def require_permission(permission: Permission) -> Callable[..., AuthenticatedUser]:
    """Dependency factory checking whether current user holds the required permission."""

    def _permission_checker(
        current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    ) -> AuthenticatedUser:
        if not has_permission(current_user.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "IZIN_DITOLAK",
                        "message": f"Peran Anda ({current_user.role}) tidak diizinkan melakukan tindakan ini.",
                        "required_permission": permission.value,
                    }
                },
            )
        return current_user

    return _permission_checker
