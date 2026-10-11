from app.services.seed import reset_demo_data, seed_all_data
from app.models.database import async_session_maker, engine, init_db
from app.models.base import Base
import asyncio
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))


async def main() -> None:
    reset_flag = "--reset" in sys.argv

    print("[INFO] Menghubungkan ke database...")
    await init_db()

    async with async_session_maker() as session:
        if reset_flag:
            print("[INFO] Menjalankan pembersihan dan inisialisasi ulang data...")
            res = await reset_demo_data(session)
            print(f"[OK] {res['message']}")
        else:
            print("[INFO] Memastikan data awal terinisialisasi...")
            summary = await seed_all_data(session)
            print(f"[OK] Selesai. Data terdaftar: {summary}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
