# db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ.get("PSQL_DB_HOST", "localhost")
DB_PORT = os.environ.get("PSQL_DB_PORT", "5432")
DB_NAME = os.environ.get("PSQL_DB_NAME", "media-db")
DB_USER = os.environ.get("PSQL_DB_USER", "mediadb_admin")
DB_PASSWORD = os.environ.get("PSQL_DB_PASSWORD", "password")


def get_database_url():
    return (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )


class Base(DeclarativeBase):
    pass


engine = create_engine(
    get_database_url(),
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()
