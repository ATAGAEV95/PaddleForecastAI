from sqlalchemy import select

from app.data.models import Users, WeatherRequests, async_session


async def get_user_by_id(user_id: int):
    """Получает пользователя из базы данных по его идентификатору.

    Выполняет асинхронный запрос к базе данных для поиска записи в таблице 'users'
    с указанным user_id. Возвращает объект пользователя или None, если пользователь
    не найден. В случае ошибки выводит сообщение об ошибке и возвращает None.

    Args:
        user_id (int): Уникальный идентификатор пользователя в Telegram.

    Returns:
        Users | None: Объект пользователя, если найден, иначе None.

    """
    try:
        async with async_session() as session:
            query = select(Users).where(Users.user_id == user_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()
    except Exception as e:
        print(f"Ошибка получения пользователя: {e}")
        return None


async def add_user(user_id: int, username: str):
    """Добавляет нового пользователя в базу данных.

    Создаёт и сохраняет новую запись в таблице 'users' с указанными user_id и username.
    В случае ошибки выводит сообщение об ошибке.

    Args:
        user_id (int): Уникальный идентификатор пользователя в Telegram.
        username (str): Имя пользователя в Telegram (может быть пустым).

    """
    try:
        async with async_session() as session:
            user = Users(user_id=user_id, username=username)
            session.add(user)
            await session.commit()
    except Exception as e:
        print(f"Ошибка добавления пользователя: {e}")


async def save_weather_request(user_id: int, forecast_text: str, ai_response: str):
    """Сохраняет запрос прогноза погоды и ответ ИИ в базу данных.

    Создаёт новую запись в таблице 'weather_requests', содержащую идентификатор пользователя,
    текст прогноза погоды и ответ ИИ-советника. В случае ошибки выводит сообщение об ошибке.

    Args:
        user_id (int): Идентификатор пользователя, сделавшего запрос.
        forecast_text (str): Текст прогноза погоды, полученный от сервиса.
        ai_response (str): Ответ ИИ-советника на основе прогноза.

    """
    try:
        async with async_session() as session:
            request = WeatherRequests(
                user_id=user_id, forecast_text=forecast_text, ai_response=ai_response
            )
            session.add(request)
            await session.commit()
    except Exception as e:
        print(f"Ошибка сохранения запроса погоды: {e}")
