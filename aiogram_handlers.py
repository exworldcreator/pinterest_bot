import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.types import FSInputFile, InputMediaPhoto
from database import connect_to_db

from database import add_user_to_db, get_all_user_ids

import os

logging.basicConfig(level=logging.INFO)

async def cmd_start(message: types.Message):
    connection = await connect_to_db()
    
    await add_user_to_db(connection, message.from_user.id, message.from_user.username)
    
    await message.answer("Hi. I'll be sending you 10 photos for inspiration hourly!")
    await message.answer("This could be where your advertising could be.")
    
    await connection.close()
    
async def send_images(bot: Bot, chat_id: int):
    folder_name = "downloaded_images"
    all_files = os.listdir(folder_name)
    first_5_files = all_files[:5]
    
    media_group = []
    
    for file in first_5_files:
        file_path = os.path.join(folder_name, file)
        
        if file.lower().endswith(('.jpg')):
            try:
                media_group.append(InputMediaPhoto(media=FSInputFile(file_path)))
            except Exception as e:
                print(f"Failed to add image {file}: {e}")
                
    if media_group:
        try:
            await bot.send_media_group(chat_id=chat_id, media=media_group)
        except Exception as e:
            print(f"Failed to send images to {chat_id}: {e}")
                
async def send_images_periodically(bot: Bot):
    connection = await connect_to_db()
    user_ids = await get_all_user_ids(connection)
    await connection.close()
    
    tasks = []
    for chat_id in user_ids:
        try:
            tasks.append(send_images(bot, chat_id))
        except Exception as e:
            print(f"Failed to send image to {chat_id}: {e}")
            
    await asyncio.gather(*tasks)
    await asyncio.sleep(1)

async def register_handlers(dp: Dispatcher):
    dp.message.register(cmd_start, Command("start"))
