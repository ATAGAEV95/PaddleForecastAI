import os

from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import DateTime, Text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SCHEMA = "public"


def get_engine(schema: str):
    return create_async_engine(
        DATABASE_URL, connect_args={"server_settings": {"search_path": schema}}
    )


if SCHEMA is None or SCHEMA == "":
    engine = get_engine("public")
else:
    engine = get_engine(SCHEMA)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, autoincrement=False)
    username = Column(String)


class WeatherRequests(Base):
    __tablename__ = "weather_requests"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    forecast_text = Column(Text)  # Текст прогноза от get_forecast
    ai_response = Column(Text)    # Ответ от ИИ
    created_at = Column(DateTime, default=datetime.utcnow)


async def init_models():
    """Создает таблицы в базе данных, если они не существуют"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
