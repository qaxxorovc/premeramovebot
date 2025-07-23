from aiogram import executor

from loader import dp
import middlewares, filters, handlers

from middlewares.middlewares import SubscriptionCheckMiddleware
# from middlewares.middlewares import SimpleSubscriptionMiddleware
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands
from database.create_channels import middleware_channels,bot_users,movies_data,fake_links
from daily import check_and_expire_subscriptions
from datetime import datetime
from loader import dp, bot
from database.manage_tables import connect_db
from data.config import ADMINS


dp.middleware.setup(SubscriptionCheckMiddleware())

import asyncio
import time
from datetime import datetime
from daily import check_and_expire_subscriptions
import aiocron
import json
from utils.adder_json import get_daily_users_count

@aiocron.crontab("00 01 * * *")
async def send_daily_user_stats():    
    daily_count = get_daily_users_count()
    
    text = (
        f"📊 <b>Kunlik hisobot</b>\n\n"
        f"📅 Bugun botga kirgan yangi foydalanuvchilar soni: <b>{daily_count}</b>\n\n"
        f"<i>Ushbu statistika har kuni avtomatik yuboriladi.</i>"
    )
    
    try:
        for i in ADMINS:
            await bot.send_message(i, text, parse_mode="HTML")
    except Exception as e:
        print(f"[xatolik] Adminga habar jo'natishda: {e}")

@aiocron.crontab("05 01 * * *")
async def clear_daily_users():
    file_path = "bot_information.json"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    data["daily_users_count"] = []

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print("✅ Har kuni 00:00da daily_users_count tozalandi")

async def cron_loop():
    while True:
        now = datetime.now()
        if now.hour == 19 and now.minute == 38:
            print("⏳ Cron ishga tushdi...")
            try:
                await check_and_expire_subscriptions()
            except Exception as e:
                print(f"❌ Cronda xatolik: {e}")
            await asyncio.sleep(60)
        else:
            await asyncio.sleep(10)



async def on_startup(dispatcher):
    asyncio.create_task(cron_loop())
    await set_default_commands(dispatcher)
    await on_startup_notify(dispatcher)
    await fake_links()
    await middleware_channels()
    await bot_users()
    await movies_data()

if __name__ == '__main__':
    executor.start_polling(dp,skip_updates=True,on_startup=on_startup)