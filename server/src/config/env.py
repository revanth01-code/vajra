from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


SERVER_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(SERVER_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    anthropic_api_key: str | None
    allowed_origin: str
    chroma_persist_path: str
    sqlite_db_path: str
    github_token: str | None


def load_settings() -> Settings:
    return Settings(
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY") or None,
        allowed_origin=os.environ.get("ALLOWED_ORIGIN", "http://localhost:5173"),
        chroma_persist_path=os.environ.get("CHROMA_PERSIST_PATH", "./chroma_db"),
        sqlite_db_path=os.environ.get("SQLITE_DB_PATH", "./incidentsense.db"),
        github_token=os.environ.get("GITHUB_TOKEN") or None,
    )


settings = load_settings()
