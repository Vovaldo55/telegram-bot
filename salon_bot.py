import asyncio
import aiosqlite
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from services import services, get_subcategories
from google_sheets import add_booking

TOKEN = "7639879991:AAHoQwhvD0yy4t6EM6DWiA-HoJcZsYzs44c"
ADMIN_IDS = [556918505]  # Вкажи тут свій Telegram ID

bot = Bot(token=TOKEN)
dp = Dispatcher()

DB_PATH = "users.db"

class AuthStates(StatesGroup):
    waiting_for_contact = State()
    waiting_for_name = State()

class BookingStates(StatesGroup):
    choosing_category = State()
    choosing_time = State()

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                phone TEXT,
                name TEXT
            )
        """)
        await db.commit()

@dp.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT phone, name FROM users WHERE telegram_id = ?", (message.from_user.id,)) as cursor:
            user = await cursor.fetchone()
    if user is None or user[0] is None:
        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Поділитись номером телефону", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer("Для авторизації поділіться, будь ласка, своїм номером телефону:", reply_markup=kb)
        await state.set_state(AuthStates.waiting_for_contact)
    elif user[1] is None:
        await message.answer("Як я можу звертатись до тебе? Введи своє ім'я.")
        await state.set_state(AuthStates.waiting_for_name)
    else:
        await show_main_menu(message, user[1])

@dp.message(AuthStates.waiting_for_contact, F.contact)
async def contact_handler(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    telegram_id = message.from_user.id
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO users (telegram_id, phone) VALUES (?, ?)",
            (telegram_id, phone)
        )
        await db.commit()
    await message.answer("Привіт. Це чат-бот студії краси \"Zhavoronok Space\". Як я можу звертатись до тебе?")
    await state.set_state(AuthStates.waiting_for_name)

@dp.message(AuthStates.waiting_for_name, F.text)
async def name_handler(message: types.Message, state: FSMContext):
    name = message.text.strip()
    telegram_id = message.from_user.id
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET name = ? WHERE telegram_id = ?",
            (name, telegram_id)
        )
        await db.commit()
    await show_main_menu(message, name)
    await state.clear()

async def show_main_menu(message: types.Message, name: str):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Онлайн запис"), KeyboardButton(text="Послуги та ціни")],
            [KeyboardButton(text="Мої записи"), KeyboardButton(text="Контакти")],
            [KeyboardButton(text="Акції та бонуси"), KeyboardButton(text="Залишити відгук")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        f"{name}, обери що тебе цікавить:",
        reply_markup=kb
    )

@dp.message(F.text == "Онлайн запис")
async def booking_start(message: types.Message, state: FSMContext):
    await state.set_state(BookingStates.choosing_category)
    categories = list(services.keys())
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=cat)] for cat in categories] + [[KeyboardButton(text="⬅️ Назад")]],
        resize_keyboard=True
    )
    await message.answer("На яку послугу бажаєте записатись?", reply_markup=kb)
    await state.update_data(path=[])

@dp.message(BookingStates.choosing_category, F.text)
async def booking_choose_category(message: types.Message, state: FSMContext):
    data = await state.get_data()
    path = data.get("path", [])
    text = message.text

    if text == "⬅️ Назад":
        await show_main_menu(message, (await get_user_name(message.from_user.id)))
        await state.clear()
        return

    path.append(text)
    subcategories = get_subcategories(path)

    if subcategories and len(subcategories) > 0:
        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=cat)] for cat in subcategories.keys()] + [[KeyboardButton(text="⬅️ Назад")]],
            resize_keyboard=True
        )
        await message.answer("Оберіть підкатегорію:", reply_markup=kb)
        await state.update_data(path=path)
    else:
        # Тут можна додати вибір часу, а поки що — тестовий запис
        await message.answer("Обери зручний час:", reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="найближчий (на цьому тижні)"), KeyboardButton(text="наступний тиждень")],
                [KeyboardButton(text="⬅️ Назад")]
            ],
            resize_keyboard=True
        ))
        await state.update_data(path=path)
        await state.set_state(BookingStates.choosing_time)

@dp.message(BookingStates.choosing_time, F.text)
async def booking_choose_time(message: types.Message, state: FSMContext):
    data = await state.get_data()
    path = data.get("path", [])
    time_choice = message.text

    # Тут можна реалізувати логіку вибору дати/часу, поки що — тестові значення
    chosen_date = "2025-06-29" if "найближчий" in time_choice else "2025-07-05"
    chosen_time = "14:00"

    # Отримуємо дані користувача
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT name, phone FROM users WHERE telegram_id = ?", (message.from_user.id,)) as cursor:
            user = await cursor.fetchone()
    user_name = user[0] if user else "Клієнт"
    phone = user[1] if user else ""

    # Додаємо запис у Google Sheets
    add_booking(
        name=user_name,
        phone=phone,
        telegram_username=message.from_user.username,
        service=' > '.join(path),
        date=chosen_date,
        time=chosen_time
    )

    # Надсилаємо адміну повідомлення
    for admin_id in ADMIN_IDS:
        await bot.send_message(
            admin_id,
            f"Новий запис!\nКлієнт: {user_name}\nТелефон: {phone}\nTelegram: @{message.from_user.username}\nПослуга: {' > '.join(path)}\nДата: {chosen_date}\nЧас: {chosen_time}"
        )

    await message.answer(f"Ви обрали: {' > '.join(path)}.\nДата: {chosen_date}, час: {chosen_time}.\nНезабаром з вами зв'яжеться адміністратор для підтвердження запису.")
    await show_main_menu(message, user_name)
    await state.clear()

async def get_user_name(telegram_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT name FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
            user = await cursor.fetchone()
    return user[0] if user else "Клієнт"

async def main():
    await init_db()
    print("Бот працює! Чекаю команду /start у Telegram.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())