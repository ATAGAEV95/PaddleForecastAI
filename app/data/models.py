import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SCHEMA = "public"


def get_engine(schema: str):
    """Создаёт и возвращает асинхронный движок SQLAlchemy с указанным схемой.

    Устанавливает параметр search_path в соединении, чтобы все запросы выполнялись
    в заданной схеме PostgreSQL.

    Args:
        schema (str): Название схемы в базе данных.

    Returns:
        AsyncEngine: Асинхронный движок SQLAlchemy.

    """
    return create_async_engine(
        DATABASE_URL, connect_args={"server_settings": {"search_path": schema}}
    )


if SCHEMA is None or SCHEMA == "":
    engine = get_engine("public")
else:
    engine = get_engine(SCHEMA)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy с поддержкой асинхронности.

    Наследуется от AsyncAttrs и DeclarativeBase, обеспечивая совместимость
    с асинхронным режимом работы SQLAlchemy.
    """

    pass


class Users(Base):
    """Модель пользователя в базе данных.

    Представляет таблицу 'users', хранящую идентификаторы Telegram-пользователей
    и их имена пользователей.
    """

    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, autoincrement=False)
    username = Column(String)


class WeatherRequests(Base):
    """Модель запросов к погоде в базе данных.

    Представляет таблицу 'weather_requests', хранящую историю запросов пользователей:
    прогноз погоды, ответ ИИ, временные метки и идентификатор пользователя.
    """

    __tablename__ = "weather_requests"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    forecast_text = Column(Text)
    ai_response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


async def init_models():
    """Инициализирует модели базы данных.

    Создаёт таблицы в базе данных, если они ещё не существуют.
    Использует метаданные Base для синхронизации схемы.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
