from dotenv import dotenv_values
from sqlalchemy import create_engine, engine, URL
from sqlalchemy.orm import sessionmaker


def get_engine(dotenv_path: str) -> engine.Engine:
    """
    データベース接続のためのEngineを作成する。

    Parameters
    ----------
    dotenv_path : str
        .envファイルのパス
    
    Returns
    -------
    sqlalchemy.engine.Engine
        データベース接続のためのEngine
    """
    config = dotenv_values(dotenv_path)

    url_object = URL.create(
        "postgresql+psycopg",
        username=config["POSTGRES_USER"],
        password=config["POSTGRES_PASSWORD"],  # plain (unescaped) text
        host=config.get("POSTGRES_HOST", "postgres"),
        port=config.get("POSTGRES_PORT", "5432"),
        database=config.get("POSTGRES_DB", "postgres"),
        query={"options": f"-c search_path={config.get('POSTGRES_SCHEMA', 'public')}"},
    )

    return create_engine(url_object)


def get_sessionmaker(dotenv_path: str) -> sessionmaker:
    """
    データベース接続のためのSessionを作成する。

    Parameters
    ----------
    dotenv_path : str
        .envファイルのパス
    
    Returns
    -------
    SessionLocal : sqlalchemy.orm.sessionmaker
        データベース接続のためのSession
    """
    engine = get_engine(dotenv_path)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal
