from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config.settings import DB_PATH, LOG_DIR

engine = create_engine(f'sqlite:///{DB_PATH}', future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


@event.listens_for(Engine, 'connect')
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON')
    cursor.close()


@contextmanager
def session_scope():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    from app.data import form_models, models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def reset_runtime_state(remove_logs: bool = False) -> None:
    """Reset local runtime state for a clean prototype start.

    This removes the SQLite database file and optionally clears application logs.
    """
    db_file = Path(DB_PATH)
    if db_file.exists():
        db_file.unlink()

    if remove_logs:
        log_dir = Path(LOG_DIR)
        for file_path in log_dir.glob('*.log'):
            try:
                file_path.unlink()
            except OSError:
                continue
