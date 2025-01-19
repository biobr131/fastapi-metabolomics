import os

from sqlalchemy.orm import Session

from db.session import get_sessionlocal


def strtobool(value: str) -> bool:
    """文字列をbool型に変換する。"""
    return value.lower() in ('true', 't', 'yes', 'y', 'on', '1')

DEBUG = bool(strtobool(str(os.environ.get("DEBUG", "False"))))

if DEBUG:
    DOTENV_PATH = "db/.env.dev"
else:
    DOTENV_PATH = "db/.env"


async def get_session(dotenv_path: str = DOTENV_PATH):
    SessionLocal = get_sessionlocal(dotenv_path)
    with SessionLocal() as session:
        try:
            yield session
        except:
            session.rollback()
            raise
