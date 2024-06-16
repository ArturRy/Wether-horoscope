from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs

from sqlalchemy.orm import DeclarativeBase

from sqlalchemy import (
    BigInteger,
    Integer,
    Column,
    String,
    Text,
    DateTime,
    Boolean,
    Time,
    func,
)
import os
from dotenv import load_dotenv

load_dotenv()


POSTGRES_PASSWORD = os.getenv("DB_PASSWORD")
POSTGRES_USER = os.getenv("DB_USER")
POSTGRES_DB = os.getenv("DB_NAME")
POSTGRES_HOST = os.getenv("DB_HOST")
POSTGRES_PORT = os.getenv("DB_PORT")

PG_DSN = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_async_engine(PG_DSN)
Session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase, AsyncAttrs):
    pass


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    tg_user_id = Column(BigInteger, nullable=False)
    user_name = Column(String(50))
    zodiac = Column(String(50))
    city = Column(String(50))
    reminder = Column(String(50))
    status = Column(Boolean, default=False)
    premium = Column(DateTime)
    gift = Column(Boolean, default=True)


async def init_db():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
