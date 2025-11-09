import asyncio
import logging
import os
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Пытаемся загрузить WEATHER_API из переменных окружения
logger.info("Пытаемся загрузить WEATHER_API из переменных окружения")
WEATHER_API = os.getenv("WEATHER_API")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"


async def make_weather_request(endpoint: str, params: dict[str, Any]) -> dict[str, Any] | None:
    """Вспомогательная функция для выполнения запросов к OpenWeatherMap API

    Args:
        endpoint: Конечная точка API (например, "weather" или "forecast")
        params: Параметры запроса

    Returns:
        JSON ответ от API или None в случае ошибки

    """
    # Проверяем наличие API ключа
    if not WEATHER_API:
        logger.error("WEATHER_API не найден в переменных окружения")
        return None

    # Добавляем API ключ к параметрам запроса
    params["appid"] = WEATHER_API
    # Устанавливаем метрическую систему (Цельсий, метры/сек)
    params["lang"] = "ru"  # Русский язык для описаний

    # Формируем полный URL
    url = f"{OPENWEATHER_BASE_URL}/{endpoint}"

    try:
        # Выполняем асинхронный HTTP запрос
        async with httpx.AsyncClient() as client:
            logger.info(f"Запрос к API: {url}")
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()  # Вызовет исключение при ошибке HTTP
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP ошибка: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        logger.error(f"Ошибка при запросе к API: {str(e)}")
        return None


async def get_forecast(city: str, days: int = 3, units: str = "metric") -> str | list[str]:
    """Получить прогноз погоды на несколько дней

    Args:
        city: Название города на русском или английском
        days: Количество дней для прогноза (1-5)
        units: Система измерения - "metric" (Цельсий) или "imperial" (Фаренгейт)

    Returns:
        Строка с прогнозом погоды или сырыми данными от API

    """
    logger.info(f"Запрос прогноза для города: {city} на {days} дней")

    # Ограничиваем количество дней
    days = min(max(days, 1), 5)

    # Формируем параметры запроса
    params = {
        "q": city,
        "units": units,
        "cnt": days * 8,  # API возвращает данные каждые 3 часа, 8 записей = 1 день
    }

    # Выполняем запрос к API
    data = await make_weather_request("forecast", params)

    # Обработка ошибок
    if not data:
        return f"❌ Не удалось получить прогноз для города '{city}'."

    if "cod" not in data or data["cod"] != "200":
        return f"❌ Ошибка API: {data.get('message', 'Неизвестная ошибка')}"

    # Возвращаем все полученные данные от API
    logger.info(f"Успешно получены сырые данные прогноза для {city}")

    times = ["15:00:00", "12:00:00", "09:00:00"]
    afternoon = [lst for lst in data["list"] if lst["dt_txt"].split()[1] in times]

    result = []
    for lst in afternoon:
        result.append(
            f"Дата время: {lst['dt_txt']}\n"
            f"Температура: {lst['main']['temp']}\n"
            f"Скорость ветра: {lst['wind']['speed']}\n"
            f"Влажность: {lst['main']['humidity']}\n"
            f"Условия: {lst['weather'][0]['description']}\n"
        )

    return result


async def main():
    async with asyncio.TaskGroup() as tg:
        task = tg.create_task(get_forecast("Червлённая", days=5))
    print(task.result())


if __name__ == "__main__":
    asyncio.run(main())
