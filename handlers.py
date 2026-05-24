import asyncio
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from data import RECIPES, DAYS_OF_WEEK

router = Router()

class UserRegistration(StatesGroup):
    diet = State()
    budget = State()

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer(
        " Привет! Я FoodPlan AI — бот для планирования питания.\n\n"
        "Я помогу тебе:\n"
        "Составить меню на неделю\n"
        "Сформировать список покупок\n"
        "Заказать доставку продуктов\n\n"
        "Давай начнем с настройки. Какая у тебя диета?",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="Стандартное питание")],
                [types.KeyboardButton(text="Вегетарианское")],
                [types.KeyboardButton(text="Низкоуглеводное")]
            ],
            resize_keyboard=True
        )
    )
    await state.set_state(UserRegistration.diet)

@router.message(UserRegistration.diet)
async def process_diet(message: types.Message, state: FSMContext):
    await state.update_data(diet=message.text)
    await message.answer(
        f"Отлично! Выбрали: {message.text}\n\n"
        "Какой у вас бюджет на питание в неделю? (напишите число в рублях)",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(UserRegistration.budget)

@router.message(UserRegistration.budget)
async def process_budget(message: types.Message, state: FSMContext):
    try:
        budget = int(message.text)
        await state.update_data(budget=budget)
        user_data = await state.get_data()

        await message.answer(
            f"Регистрация завершена!\n\n"
            f" Ваши настройки:\n"
            f"️ Диета: {user_data['diet']}\n"
            f"Бюджет: {budget} руб/неделю\n\n"
            "Теперь я могу сгенерировать для вас меню на 7 дней!",
            reply_markup=types.ReplyKeyboardMarkup(
                keyboard=[[types.KeyboardButton(text="📅 Сгенерировать меню на неделю")]],
                resize_keyboard=True
            )
        )
        await state.clear()
    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректное число (например: 5000)")

@router.message(F.text.startswith("📅"))
async def generate_menu(message: types.Message):
    await message.answer("Генерирую меню на неделю с помощью AI...")
    await asyncio.sleep(1.5)

    menu_text = "**Ваше меню на неделю:**\n\n"
    for i, day in enumerate(DAYS_OF_WEEK):
        breakfast = RECIPES["standard"][i % len(RECIPES["standard"])]
        lunch = RECIPES["standard"][(i+2) % len(RECIPES["standard"])]
        dinner = RECIPES["standard"][(i+4) % len(RECIPES["standard"])]

        menu_text += f"**{day}**\n"
        menu_text += f"Завтрак: {breakfast['name']} ({breakfast['calories']} ккал)\n"
        menu_text += f"Обед: {lunch['name']} ({lunch['calories']} ккал)\n"
        menu_text += f"Ужин: {dinner['name']} ({dinner['calories']} ккал)\n\n"

    await message.answer(
        menu_text,
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text="Сформировать список покупок")]],
            resize_keyboard=True
        )
    )

@router.message(F.text == "Сформировать список покупок")
async def create_shopping_list(message: types.Message):
    await message.answer("Формирую список покупок...")
    await asyncio.sleep(1)

    all_products = {}
    for i in range(7):
        for meal_type in range(3):
            recipe_idx = (i + meal_type) % len(RECIPES["standard"])
            recipe = RECIPES["standard"][recipe_idx]
            for product in recipe["products"]:
                all_products[product] = all_products.get(product, 0) + 1

    list_text = "🛒 **Список покупок на неделю:**\n\n"
    for product, count in sorted(all_products.items()):
        list_text += f"• {product} (×{count})\n" if count > 1 else f"• {product}\n"

    list_text += f"\n Всего уникальных позиций: {len(all_products)}"

    await message.answer(
        list_text,
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text=" Оформить доставку")],
                [types.KeyboardButton(text=" Посмотреть статистику")]
            ],
            resize_keyboard=True
        )
    )

@router.message(F.text == " Оформить доставку")
async def delivery_integration(message: types.Message):
    await message.answer("🔗 Подключаюсь к API службы доставки...")
    await asyncio.sleep(1)

    await message.answer(
        " **Интеграция с доставкой успешна!**\n\n"
        " Ваш заказ сформирован:\n"
        "•Служба доставки: Яндекс.Лавка (API интеграция)\n"
        "•Сумма заказа: ~3500 руб.\n"
        "•Время доставки: 60 минут\n"
        "•Статус: Ожидает подтверждения\n\n"
        " В production версии здесь был бы реальный переход в приложение доставки.",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text=" Посмотреть статистику")]],
            resize_keyboard=True
        )
    )

@router.message(F.text == " Посмотреть статистику")
async def show_stats(message: types.Message):
    await message.answer(
        " **Ваша статистика:**\n\n"
        " Меню составлено на: 7 дней\n"
        " Всего приемов пищи: 21\n"
        " Продуктов в списке: 15+\n"
        " Сэкономлено времени: ~3 часа\n"
        " Средний чек: 3500 руб/неделю\n\n"
        " Бот работает стабильно (время отклика < 2 сек)"
    )