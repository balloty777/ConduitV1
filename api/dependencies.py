from collections.abc import Generator
from database.database import get_session
from sqlalchemy.orm import Session
def get_db()->Generator[Session,None,None]:
    with get_session() as db:
        yield db