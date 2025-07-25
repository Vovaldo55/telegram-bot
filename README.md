# Telegram Bot з API інтеграцією

Цей бот надає наступні функції:
- 🌤️ Погода для будь-якого міста
- 💱 Курс валют USD/UAH
- 😄 Смішні українські жарти
- 📞 Контактна інформація

## 🚀 Розгортання на Render (Безкоштовно)

### Крок 1: Підготовка GitHub
1. Створіть репозиторій на GitHub
2. Завантажте цей код у репозиторій
3. Переконайтеся, що файл `.env` НЕ завантажений (він в `.gitignore`)

### Крок 2: Налаштування Render
1. Перейдіть на [render.com](https://render.com)
2. Зареєструйтесь (можна через GitHub)
3. Натисніть "New +" → "Web Service"
4. Підключіть ваш GitHub репозиторій

### Крок 3: Налаштування змінних середовища
1. У розділі "Environment Variables" додайте:
   - **Key:** `BOT_TOKEN`
   - **Value:** ваш токен бота (без лапок)

### Крок 4: Налаштування сервісу
- **Name:** telegram-bot
- **Environment:** Python 3
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python bot.py`

### Крок 5: Запуск
1. Натисніть "Create Web Service"
2. Дочекайтесь завершення розгортання (5-10 хвилин)
3. Ваш бот буде працювати 24/7!

## 💰 Безкоштовний план Render:
- **750 годин на місяць** (31 день × 24 години = 744 години)
- **Достатньо для 24/7 роботи** весь місяць
- **Автоматичне перезапуск** при помилках
- **Логи в реальному часі**

## 🔧 Локальне тестування

1. **Встановіть залежності:**
```bash
pip install aiogram aiohttp python-dotenv
```

2. **Створіть файл `.env`:**
```
BOT_TOKEN=ваш_токен_бота_тут
```

3. **Запустіть бота:**
```bash
python bot.py
```

## 🔒 Безпека

⚠️ **ВАЖЛИВО:** 
- Ніколи не додавайте токен бота безпосередньо в код!
- Використовуйте змінні середовища
- Файл `.env` вже додано до `.gitignore`
- Не публікуйте токени в публічних репозиторіях

## 📊 Функції

### Погода
- Введіть назву міста
- Отримайте поточну погоду

### Курс валют
- Реальний курс USD до UAH
- Оновлюється автоматично

### Жарти
- Українські жарти про програмування
- Резервна база жартів, якщо API недоступний

### Контакти
- Контактна інформація 