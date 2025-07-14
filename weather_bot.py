
import asyncio
import aiohttp
import json
import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import os
from dotenv import load_dotenv
# ... інші імпорти ...

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Погода"), KeyboardButton(text="Курс валют")],
        [KeyboardButton(text="Жарт"), KeyboardButton(text="Контакти")]
    ],
    resize_keyboard=True
)


class WeatherStates(StatesGroup):
    waiting_for_city = State()


# Функція для отримання погоди
async def get_weather(city):
    try:
        url = f"https://wttr.in/{city}?format=3"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    weather = await response.text()
                    return weather.strip()
                else:
                    return "Не вдалося отримати погоду для цього міста."
    except Exception as e:
        return f"Помилка при отриманні погоди: {str(e)}"


# База українських жартів
ukrainian_jokes = [
    "Чому програміст ходить до лікаря? Бо у нього проблеми з пам'яттю!",
    "Як програміст ловить рибу? Використовує інтернет!",
    "Що сказав програміст, коли його запитали про здоров'я? 'Все працює, але є баги!'",
    "Чому комп'ютер не може знайти файл? Бо він забув шлях!",
    "Як програміст готує каву? Ctrl+C, Ctrl+V!",
    "Чому діти люблять програмування? Бо там можна робити баги і ніхто не свариться!",
    "Що сказав програміст після весілля? 'Тепер потрібно оновити статус!'",
    "Як програміст вирішує проблеми? Перезавантажує систему!",
    "Чому програміст не може знайти ключі? Бо він не зробив backup!",
    "Що робить програміст у вільний час? Програмує!",
    "Як програміст замовляє піцу? Через API!",
    "Чому програміст не може спати? Бо у нього нескінченний цикл думок!",
    "Що сказав програміст, коли його запитали про досвід? 'У мене 5 років стажу, але 10 років багів!'",
    "Як програміст знаходить помилку? Методом проб і помилок!",
    "Чому програміст не може знайти дружину? Бо він шукає в неправильній папці!"
]

# Функція для отримання жарту
async def get_joke():
    try:
        # Спочатку спробуємо отримати жарт з API
        url = "https://v2.jokeapi.dev/joke/Programming?lang=uk"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('joke'):
                        return f"Жарт:\n{data['joke']}"
                    elif data.get('setup') and data.get('delivery'):
                        return f"Жарт:\n{data['setup']}\n\n{data['delivery']}"
                    else:
                        # Якщо API не працює, використовуємо нашу базу
                        return f"Жарт:\n{random.choice(ukrainian_jokes)}"
                else:
                    # Якщо API не працює, використовуємо нашу базу
                    return f"Жарт:\n{random.choice(ukrainian_jokes)}"
    except Exception as e:
        # У випадку помилки використовуємо нашу базу
        return f"Жарт:\n{random.choice(ukrainian_jokes)}"


# Функція для отримання курсу валют
async def get_currency():
    try:
        # Спробуємо інший API для курсів валют
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    usd_to_uah = data["rates"]["UAH"]
                    return f"Курс USD до UAH: {usd_to_uah:.2f}"
                else:
                    return "Не вдалося отримати курс валют."
    except Exception as e:
        return f"Помилка при отриманні курсу валют: {str(e)}"


@dp.message(lambda message: message.text == "/start")
async def start_handler(message: types.Message):
    await message.answer("Оберіть опцію:", reply_markup=main_kb)


@dp.message(lambda message: message.text == "Погода")
async def weather_handler(message: types.Message, state: FSMContext):
    await message.answer("Введіть місто для отримання погоди:")
    await state.set_state(WeatherStates.waiting_for_city)


@dp.message(WeatherStates.waiting_for_city)
async def show_weather(message: types.Message, state: FSMContext):
    city = message.text
    await message.answer("Отримую погоду...")

    weather = await get_weather(city)
    await message.answer(weather)
    await state.clear()


@dp.message(lambda message: message.text == "Курс валют")
async def currency_handler(message: types.Message):
    await message.answer("Отримую курс валют...")

    currency = await get_currency()
    await message.answer(currency)


@dp.message(lambda message: message.text == "Жарт")
async def joke_handler(message: types.Message):
    await message.answer("Отримую жарт...")

    joke = await get_joke()
    await message.answer(joke)


@dp.message(lambda message: message.text == "Контакти")
async def contacts_handler(message: types.Message):
    await message.answer("Контакти: Київ, вул. Краси, 1\nТелефон: +380 99 123 45 67")


@dp.message()
async def fallback(message: types.Message):
    await message.answer("Оберіть опцію з меню:", reply_markup=main_kb)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())