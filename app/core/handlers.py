from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from app.core.weather_advisor import ai_generate
from app.data.request import add_user, get_user_by_id
from app.tools.utils import hash_password

router = Router()


ACCESS_PASSWORD = "e5ae93bd8095fbd86c25a110bbf194a5a1a209f1e8eb31bb30c8b0ecbe254d58"


class RegisterState(StatesGroup):
    """Группа состояний для процесса регистрации пользователя.

    Содержит состояния, используемые в конечном автомате (FSM) при авторизации.
    """

    waiting_for_password = State()


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    """Обработчик команды /start.

    Проверяет, существует ли пользователь в базе данных.
    Если существует — приветствует. Если нет — запрашивает пароль доступа
    и переводит пользователя в состояние ожидания ввода пароля.

    Args:
        message (Message): Объект входящего сообщения от пользователя.
        state (FSMContext): Контекст состояния конечного автомата.

    """
    user_id = message.from_user.id
    user = await get_user_by_id(user_id)
    if user:
        await message.answer("Добро пожаловать!")
    else:
        await message.answer("Добро пожаловать! Для продолжения работы введите пароль для доступа.")
        await state.set_state(RegisterState.waiting_for_password)


@router.message(RegisterState.waiting_for_password)
async def password_handler(message: Message, state: FSMContext):
    """Обработчик ввода пароля при регистрации.

    Проверяет хешированный ввод пользователя на соответствие
    заранее заданному хешу ACCESS_PASSWORD. При успехе — добавляет
    пользователя в базу данных, отправляет подтверждение и очищает состояние.
    Иначе — запрашивает ввод пароля повторно.

    Args:
        message (Message): Сообщение с введённым паролем.
        state (FSMContext): Контекст состояния конечного автомата.

    """
    user_id = message.from_user.id
    if hash_password(message.text.strip()) == ACCESS_PASSWORD:
        await add_user(user_id, message.from_user.username or "")
        await message.answer("Авторизация успешна! Теперь у вас полный доступ.")
        await state.clear()
    else:
        await message.answer("Неверный пароль. Попробуйте еще раз:")


from app.data.request import save_weather_request
from app.services.weather import get_forecast  # Добавьте этот импорт


@router.message(Command("get"))
async def get_generate(message: Message):
    """Обработчик команды /get.

    Получает прогноз погоды для города Червлённая на 5 дней,
    передаёт его в систему ИИ-советника, сохраняет запрос и ответ в базу,
    затем отправляет пользователю результат совета.

    Args:
        message (Message): Входящее сообщение с командой /get.

    """
    weather_forecast = await get_forecast("Червлённая", days=5)

    if isinstance(weather_forecast, list):
        weather_forecast = "\n".join(weather_forecast)

    result = await ai_generate(weather_forecast)

    await save_weather_request(
        user_id=message.from_user.id, forecast_text=weather_forecast, ai_response=result
    )

    await message.answer(result)
