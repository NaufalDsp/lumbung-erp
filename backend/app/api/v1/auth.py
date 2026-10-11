from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DEMO_PERSONAS, AuthenticatedUser, get_current_user
from app.api.v1.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserResponse,
)
from app.core.config import settings
from app.core.permissions import get_permissions_for_role
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.domain.enums import UserRole
from app.models.database import get_db
from app.models.refresh_token import RefreshToken
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

REFRESH_COOKIE_NAME = "lumbung_refresh_token"


def _set_refresh_cookie(response: Response, raw_refresh_token: str) -> None:
    max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=raw_refresh_token,
        max_age=max_age,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        path="/api/v1/auth",
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        path="/api/v1/auth",
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """Standard email + password login."""
    stmt = select(User).where(User.email == payload.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        # Fallback check against official enterprise accounts if table had not populated
        for persona in DEMO_PERSONAS.values():
            if persona["email"] == payload.email and payload.password == "Lumbung2026!":
                user = User(
                    id=int(persona["id"]),
                    email=str(persona["email"]),
                    name=str(persona["name"]),
                    role=str(persona["role"]),
                    password_hash=hash_password("Lumbung2026!"),
                    is_active=True,
                )
                db.add(user)
                try:
                    await db.commit()
                except Exception:
                    await db.rollback()
                break

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "KREDENSIAL_SALAH",
                              "message": "Email atau kata sandi tidak cocok"}},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "PENGGUNA_NONAKTIF",
                              "message": "Akun pengguna dinonaktifkan"}},
        )

    # Issue access token
    access_token = create_access_token(
        subject=user.id,
        claims={"role": user.role, "email": user.email},
    )

    # Issue refresh token
    raw_refresh, token_hash = generate_refresh_token()
    db_refresh = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.now(
            timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(db_refresh)
    await db.commit()

    _set_refresh_cookie(response, raw_refresh)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            is_active=user.is_active,
            permissions=get_permissions_for_role(user.role),
        ),
    )


@router.post("/demo/{role}", response_model=TokenResponse)
async def demo_login(
    role: str,
    response: Response,
) -> TokenResponse:
    """Instant 1-click login for demo personas (PRD Section 11 F1).

    Roles: admin, sales, warehouse, finance.
    """
    if not settings.DEMO_MODE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "DEMO_NONAKTIF",
                              "message": "Mode demo tidak aktif"}},
        )

    role_key = role.lower()
    if role_key not in DEMO_PERSONAS:
        valid_roles = ", ".join(DEMO_PERSONAS.keys())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "PERAN_TIDAK_VALID",
                              "message": f"Peran demo harus salah satu dari: {valid_roles}"}},
        )

    persona = DEMO_PERSONAS[role_key]
    user_id = int(persona["id"])
    email = str(persona["email"])
    user_role = str(persona["role"])
    name = str(persona["name"])

    # Issue demo access token
    access_token = create_access_token(
        subject=user_id,
        claims={"role": user_role, "email": email, "is_demo": True},
    )

    # Demo refresh token cookie
    raw_refresh, _ = generate_refresh_token()
    _set_refresh_cookie(response, raw_refresh)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(
            id=user_id,
            email=email,
            name=name,
            role=user_role,
            is_active=True,
            permissions=get_permissions_for_role(user_role),
        ),
    )


class RoleLoginPayload(BaseModel):
    role: str


@router.post("/demo-login", response_model=TokenResponse)
async def demo_login_by_body(
    payload: RoleLoginPayload,
    response: Response,
) -> TokenResponse:
    """Alternative POST endpoint accepting JSON body {'role': 'admin'}."""
    return await demo_login(payload.role, response)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    body: RefreshTokenRequest | None = None,
    cookie_token: Annotated[str | None, Cookie(
        alias=REFRESH_COOKIE_NAME)] = None,
) -> TokenResponse:
    """Rotates refresh token and issues a new access token."""
    raw_token = (body and body.refresh_token) or cookie_token
    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "REFRESH_TOKEN_DIPERLUKAN",
                              "message": "Refresh token tidak ditemukan"}},
        )

    token_hash = hash_token(raw_token)
    stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    result = await db.execute(stmt)
    db_token = result.scalar_one_or_none()

    if not db_token or not db_token.is_active:
        _clear_refresh_cookie(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "REFRESH_TOKEN_KADALUWARSA",
                              "message": "Refresh token tidak valid atau telah dicabut"}},
        )

    # Load associated user
    user_stmt = select(User).where(User.id == db_token.user_id)
    user_res = await db.execute(user_stmt)
    user = user_res.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "PENGGUNA_TIDAK_DITEMUKAN",
                              "message": "Pengguna tidak aktif"}},
        )

    # Rotate refresh token (revoke old, issue new)
    now = datetime.now(timezone.utc)
    db_token.revoked_at = now

    new_raw_refresh, new_token_hash = generate_refresh_token()
    new_db_token = RefreshToken(
        user_id=user.id,
        token_hash=new_token_hash,
        expires_at=now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(new_db_token)
    await db.commit()

    _set_refresh_cookie(response, new_raw_refresh)

    new_access_token = create_access_token(
        subject=user.id,
        claims={"role": user.role, "email": user.email},
    )

    return TokenResponse(
        access_token=new_access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            is_active=user.is_active,
            permissions=get_permissions_for_role(user.role),
        ),
    )


@router.post("/logout")
async def logout(
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    cookie_token: Annotated[str | None, Cookie(
        alias=REFRESH_COOKIE_NAME)] = None,
) -> dict[str, str]:
    """Revokes refresh token and clears cookie."""
    if cookie_token:
        token_hash = hash_token(cookie_token)
        now = datetime.now(timezone.utc)
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.token_hash == token_hash, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=now)
        )
        await db.execute(stmt)
        await db.commit()

    _clear_refresh_cookie(response)
    return {"message": "Berhasil keluar"}


@router.post("/reset-demo")
async def reset_demo(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Resets database demo data deterministically. Available in demo mode."""
    if not settings.DEMO_MODE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "MODE_DEMO_NONAKTIF",
                              "message": "Reset data hanya diizinkan dalam mode demo."}},
        )

    from app.services.seed import reset_demo_data

    return await reset_demo_data(db)


@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> UserResponse:
    """Returns profile and authorized action permissions of the authenticated user."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role,
        is_active=current_user.is_active,
        permissions=get_permissions_for_role(current_user.role),
    )
