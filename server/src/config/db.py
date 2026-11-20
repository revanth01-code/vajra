from pathlib import Path

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from src.config.env import SERVER_ROOT, settings
from src.models.feedback import Feedback
from src.models.investigation import Investigation


def _database_url() -> str:
    database_path = Path(settings.sqlite_db_path)
    if not database_path.is_absolute():
        database_path = SERVER_ROOT / database_path
    database_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{database_path.as_posix()}"


engine = create_engine(_database_url(), connect_args={"check_same_thread": False})


def initialize_database() -> None:
    Investigation.metadata.create_all(engine)


def get_investigation_count() -> int:
    with Session(engine) as session:
        return session.scalar(select(func.count()).select_from(Investigation)) or 0
