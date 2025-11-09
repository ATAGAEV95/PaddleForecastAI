from sqlalchemy import select

from app.data.models import Users, async_session


async def get_user_by_id(user_id: int):
    try:
        async with async_session() as session:
            query = select(Users).where(Users.user_id == user_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()
    except Exception as e:
        print(f"Ошибка получения пользователя: {e}")
        return None


async def add_user(user_id: int, username: str):
    try:
        async with async_session() as session:
            user = Users(user_id=user_id, username=username)
            session.add(user)
            await session.commit()
    except Exception as e:
        print(f"Ошибка добавления пользователя: {e}")
