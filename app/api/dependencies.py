import os

from sqlalchemy.orm import Session

from db.session import get_sessionmaker


def get_session(dotenv_path: str) -> Session:
    SessionLocal = get_sessionmaker(dotenv_path)
    return SessionLocal()


async def get_session_prod():
    with get_session("db/.env") as session:
        try:
            yield session
        except:
            session.rollback()
            raise


async def get_session_dev():
    with get_session("db/.env.dev") as session:
        try:
            yield session
        except:
            session.rollback()
            raise
