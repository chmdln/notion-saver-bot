import os
import asyncio
from aiogram import Bot, Dispatcher
from handlers.commands import router 

from dotenv import find_dotenv, load_dotenv 
load_dotenv(find_dotenv())
from database.engine import create_db






async def main():
    bot = Bot(token=os.getenv('BOT_TOKEN'))
    dp = Dispatcher()    
    dp.include_routers(router)

    await create_db()
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())  



if __name__ == '__main__':
    asyncio.run(main())
