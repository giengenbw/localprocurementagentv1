from __future__ import annotations
import os
from contextlib import contextmanager
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from database.models import Base

def _sqlite_path(url: str) -> None:
    if url.startswith("sqlite:///"):
        raw = url.removeprefix("sqlite:///")
        if raw != ":memory:":
            Path(raw).parent.mkdir(parents=True, exist_ok=True)

def create_db_engine(url: str | None = None):
    url = url or os.getenv("DATABASE_URL", "sqlite:///./data/procurement.db")
    _sqlite_path(url)
    kwargs = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=kwargs)

ENGINE = create_db_engine()
SessionLocal = sessionmaker(bind=ENGINE, expire_on_commit=False)

def init_db(engine=ENGINE) -> None:
    Base.metadata.create_all(engine)

@contextmanager
def session_scope(factory=SessionLocal):
    session: Session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
