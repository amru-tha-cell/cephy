from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import DB_URL

_engine_args = (
    {"connect_args": {"check_same_thread": False}}
    if DB_URL.startswith("sqlite")
    else {}
)

engine = create_engine(DB_URL, **_engine_args)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()