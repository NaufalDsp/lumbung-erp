import logging
import socket
from collections.abc import AsyncGenerator
from urllib.parse import urlparse

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

logger = logging.getLogger(__name__)

SQLITE_FALLBACK_URL = "sqlite+aiosqlite:///./lumbung.db"


def _resolve_database_url() -> str:
    url = settings.DATABASE_URL
    if url.startswith("sqlite"):
        return url

    # If Postgres URL, test if host/port is reachable
    try:
        clean_url = url.replace("+asyncpg", "")
        parsed = urlparse(clean_url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 5432
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        is_open = sock.connect_ex((host, port)) == 0
        sock.close()
        if is_open:
            return url
    except Exception:
        pass

    logger.warning(
        f"[DATABASE] Server PostgreSQL ({url}) tidak aktif. "
        f"Menggunakan database lokal SQLite: {SQLITE_FALLBACK_URL}"
    )
    return SQLITE_FALLBACK_URL


ACTIVE_DATABASE_URL = _resolve_database_url()

engine = create_async_engine(
    ACTIVE_DATABASE_URL,
    echo=False if ACTIVE_DATABASE_URL.startswith("sqlite") else settings.DEBUG,
    future=True,
    pool_pre_ping=not ACTIVE_DATABASE_URL.startswith("sqlite"),
)

# Async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def init_db() -> None:
    """Initializes tables and auto-seeds initial enterprise records if empty."""
    from app.models.base import Base
    import app.models  # register all models
    from app.models.user import User
    from app.services.seed import seed_all_data

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        result = await session.execute(select(User).limit(1))
        existing_user = result.scalar_one_or_none()
        if not existing_user:
            logger.info(
                "[DATABASE] Database baru terdeteksi. Menjalankan inisialisasi akun resmi...")
            await seed_all_data(session)
            logger.info("[DATABASE] Inisialisasi data akun resmi selesai.")


async def close_db() -> None:
    """Closes all database connections."""
    global engine
    if engine:
        await engine.dispose()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency yielding an async database session per request."""
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
