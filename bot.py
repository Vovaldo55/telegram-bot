from services import services, get_subcategories

class BookingStates(StatesGroup):
    choosing_category = State()
    choosing_subcategory = State()

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

    # Додаємо вибір до шляху
    path.append(text)
    subcategories = get_subcategories(path)

    if subcategories and len(subcategories) > 0:
        # Є підкатегорії, показуємо їх
        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=cat)] for cat in subcategories.keys()] + [[KeyboardButton(text="⬅️ Назад")]],
            resize_keyboard=True
        )
        await message.answer("Оберіть підкатегорію:", reply_markup=kb)
        await state.update_data(path=path)
    else:
        # Кінцева послуга
        await message.answer(f"Ви обрали: {' > '.join(path)}.\nНезабаром з вами зв'яжеться адміністратор для підтвердження запису.")
        await show_main_menu(message, (await get_user_name(message.from_user.id)))
        await state.clear()
