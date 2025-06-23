from aiogram import types
from loader import bot

async def check_subscription(user_id: int, channel_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        if member.status in ("member", "administrator", "creator"):
            return True
        else:
            return False
    except Exception as e:
        print(f"check_subscription xatolik: {e}")
        return False
