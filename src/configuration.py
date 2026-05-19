import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the repository root (parent of src/).
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)

CONNECTION_STRING = os.getenv(
    "DATABASE_URL",
    os.getenv(
        "CONNECTION_STRING",
        "postgresql+psycopg://fraud:fraud@localhost:5432/fraud",
    ),
)
TIME_WINDOW = os.getenv("TIME_WINDOW", "1h")
BATCH_COUNT = int(os.getenv("BATCH_COUNT", "100"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _resolve_path(path: str) -> Path:
    resolved = Path(path)
    return resolved if resolved.is_absolute() else _PROJECT_ROOT / resolved


LOG_FILE = _resolve_path(os.getenv("LOG_FILE", "logs/fraud-detector.log"))
LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", str(10 * 1024 * 1024)))
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-only-change-before-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60")
)
