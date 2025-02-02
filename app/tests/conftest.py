from pathlib import Path
from typing import Generator

import pytest
from contextlib import contextmanager
from dotenv import dotenv_values
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, engine, URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

from app.main import app

BASE_DIR = Path(__file__).parent.parent
config = dotenv_values(f"{BASE_DIR} / db / .env.test")
TEST_DATABASE_URL = URL.create(
        "postgresql+psycopg",
        username=config["TEST_POSTGRES_USER"],
        password=config["TEST_POSTGRES_PASSWORD"],  # plain (unescaped) text
        host=config.get("TEST_POSTGRES_HOST", "postgres"),
        port=config.get("TEST_POSTGRES_PORT", "5432"),
        database=config.get("TEST_POSTGRES_DB", "test_postgres"),
        query={"options": f"-c search_path={config.get('TEST_POSTGRES_SCHEMA', 'public')}"},
    )


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """テストデータベースの作成と削除を管理"""
    if database_exists(TEST_DATABASE_URL):
        drop_database(TEST_DATABASE_URL)
    
    create_database(TEST_DATABASE_URL)
    yield
    drop_database(TEST_DATABASE_URL)


@pytest.fixture
def test_get_engine() -> Generator[engine.Engine, None, None]:
    engine = create_engine(
        TEST_DATABASE_URL, pool_size=5, max_overflow=10, pool_timeout=30, pool_recycle=1000
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@contextmanager
def get_session(engine) -> Generator[sessionmaker, None, None]:
    """トランザクション分離されたセッションを提供するコンテキストマネージャ"""
    with engine.connect() as connection:
        with connection.begin() as transaction:
            TestingSessionLocal = sessionmaker(
                bind=connection,
                autocommit=False,
                autoflush=False
            )
            with TestingSessionLocal() as session:
                try:
                    yield session
                except:
                    transaction.rollback()
                    raise


@pytest.fixture(scope="function")
def test_get_session(test_engine) -> Generator[sessionmaker, None, None]:
    """セッションフィクスチャ"""
    with get_session(test_engine) as session:
        yield session


@pytest.fixture(scope="function")
def test_client() -> Generator[TestClient, None, None]:
    """テストクライアントを提供するフィクスチャ"""
    with TestClient(app) as client:
        yield client
