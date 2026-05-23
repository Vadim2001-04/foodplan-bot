import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from config import BOT_TOKEN
import handlers

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def main():
    """Точка входа в приложение"""
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Регистрируем роутер с хендлерами
    dp.include_router(handlers.router)

    logging.info("Бот запущен...")

    # Запускаем polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())