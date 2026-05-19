#!/usr/bin/env python3
"""Container entrypoint: wait for DB, seed if empty, then start uvicorn."""
import os
import subprocess
import sys
import time
from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import OperationalError

APP_SRC = Path("/app/src")
DEFAULT_DATABASE_URL = "postgresql+psycopg://fraud:fraud@db:5432/fraud"


def get_database_url() -> str:
    return os.getenv(
        "DATABASE_URL",
        os.getenv("CONNECTION_STRING", DEFAULT_DATABASE_URL),
    )


def wait_for_database(url: str, max_attempts: int = 30, delay: float = 2.0) -> None:
    engine = create_engine(url)
    try:
        for attempt in range(1, max_attempts + 1):
            try:
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                print("Database is ready", flush=True)
                return
            except OperationalError:
                if attempt == max_attempts:
                    raise
                print(
                    f"Waiting for database ({attempt}/{max_attempts})...",
                    flush=True,
                )
                time.sleep(delay)
    finally:
        engine.dispose()


def database_needs_seed(url: str) -> bool:
    engine = create_engine(url)
    try:
        return "user" not in inspect(engine).get_table_names()
    finally:
        engine.dispose()


def main() -> None:
    os.chdir(APP_SRC)
    sys.path.insert(0, str(APP_SRC))

    database_url = get_database_url()
    wait_for_database(database_url)

    if database_needs_seed(database_url):
        print("Database is empty, running seed...", flush=True)
        subprocess.check_call([sys.executable, "seed.py"])

    os.execvp(
        "uvicorn",
        ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"],
    )


if __name__ == "__main__":
    main()
