import asyncio

from config import bot, dp
from handlers import router
from functions import update_tracked_products


async def main():
    _ = asyncio.create_task(update_tracked_products())
    dp.include_router(router)
    print('Бот успешно запущен')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
