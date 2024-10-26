import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from prometheus_client import start_http_server
from app.handlers import router
from app.database.models import async_main
from app.conf.redis import redis_client 
from app.database.backup import backup_database

logging.basicConfig(
    filename='bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

load_dotenv()

async def main():
    await async_main()

    await backup_database()

    bot = Bot(token=os.getenv('TG_TOKEN'))
    dispatcher = Dispatcher()
    dispatcher.include_router(router)

    print("Бот запущенa и готов к работе.")
    logging.info("Bot started and ready to work.")

    await dispatcher.start_polling(bot)

if __name__ == '__main__':
    start_http_server(8000)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('Bot stopped')
        print('Бот выключен')
