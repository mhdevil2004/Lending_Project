

import os
import sys
import threading
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV_PYTHON = ROOT / "venv" / "Scripts" / "python.exe"


def _use_venv() -> None:
    """Re-launch with venv Python so dependencies match requirements.txt."""
    if VENV_PYTHON.exists() and Path(sys.executable).resolve() != VENV_PYTHON.resolve():
        os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__, *sys.argv[1:]])


def _check_database() -> bool:
    from sqlalchemy import create_engine, text

    from app.core.config import get_settings

    settings = get_settings()
    try:
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine.dispose()
        return True
    except Exception as exc:
        print("\n  ERROR: Cannot connect to PostgreSQL.")
        print(f"  Host: {settings.DATABASE_HOST}:{settings.DATABASE_PORT}")
        print(f"  Database: {settings.DATABASE_NAME}")
        print(f"  Details: {exc}")
        print("\n  Update .env with your PostgreSQL credentials, then run: py app.py\n")
        return False


def _open_browser() -> None:
    time.sleep(1.5)
    webbrowser.open("http://localhost:8000")


if __name__ == "__main__":
    _use_venv()

    if not _check_database():
        sys.exit(1)

    import uvicorn

    print("\n  Lending Customer Management")
    print("  Dashboard: http://localhost:8000")
    print("  API Docs:  http://localhost:8000/docs\n")

    threading.Thread(target=_open_browser, daemon=True).start()
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
