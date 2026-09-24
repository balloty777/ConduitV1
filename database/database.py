from sqlalchemy import create_engine
from contextlib import contextmanager
from core.config import settings
from sqlalchemy.orm import DeclarativeBase, sessionmaker,Session
from collections.abc import Generator
engine=create_engine(settings.database_url)
class Base(DeclarativeBase):
    pass
SessionLocal=sessionmaker(bind=engine)

@contextmanager
def get_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()