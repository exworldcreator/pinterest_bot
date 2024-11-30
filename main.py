import asyncio
import logging
from aiogram import Bot, Dispatcher
import aiogram_handlers, image_collection
from aiogram_handlers import register_handlers
from database import connect_to_db, create_user_table
from dotenv import load_dotenv
import os

load_dotenv()

bot = Bot(token=os.getenv("API_TOKEN"))
dp = Dispatcher(bot=bot)

logging.basicConfig(level=logging.INFO)

async def run_every_hour():
    while True:
        await image_collection.main()
        await aiogram_handlers.send_images_periodically(bot)
        await asyncio.sleep(5)

async def main():
    connection = await connect_to_db()
    
    if connection:
        await create_user_table(connection)
        await connection.close()
        
    asyncio.create_task(run_every_hour())
            
    await register_handlers(dp)
    await dp.start_polling(bot)
    
if __name__ == '__main__':
    asyncio.run(main())
