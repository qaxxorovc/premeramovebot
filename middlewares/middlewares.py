import random
from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loader import bot
from data.config import BOTUSERNAME
from filters.filters import IsAdmin
from database.manage_tables import get_mdd_channels

EMOJIS = ['🔥', '🌟', '💥', '🎉', '✨', '🚀', '😎', '🎈', '🍀', '💫']

async def is_bot_admin_in_channel(channel_id: int) -> bool:
    try:
        member = await bot.get_chat_member(channel_id, bot.id)
        return member.status in ("administrator", "creator")
    except Exception as e:
        print(f"[is_bot_admin_in_channel] Cannot verify admin in channel {channel_id}: {e}")
        return False

async def check_subscription(user_id: int, channel_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception as e:
        print(f"[check_subscription] Cannot check user {user_id} in channel {channel_id}: {e}")
        return False

async def generate_subscription_buttons(unsubscribed_channels: dict):
    """Create inline buttons only for unsubscribed channels where bot is admin"""
    channels_markup = InlineKeyboardMarkup(row_width=1)
    for channel_id, channel in unsubscribed_channels.items():
        channel_name = channel["name"]
        channel_username = channel["username"]
        channel_url = f"https://t.me/{channel_username}"
        emoji = random.choice(EMOJIS)
        button = InlineKeyboardButton(text=f"{channel_name} {emoji}", url=channel_url)
        channels_markup.add(button)

    check_button = InlineKeyboardButton(text="Tekshirish ♻️", url=f"https://t.me/{BOTUSERNAME}?start=restart")
    channels_markup.add(check_button)

    return channels_markup

class SubscriptionCheckMiddleware(BaseMiddleware):
    async def on_process_update(self, update: types.Update, data: dict):
        message = update.message or (update.callback_query.message if update.callback_query else None)
        if not message:
            return

        user_id = message.from_user.id

        if await IsAdmin()(message):
            return

        all_channels = await get_mdd_channels()
        
        if not all_channels:
            return
        
        unsubscribed_channels = {}

        for channel_id, channel in all_channels.items():
            channel_id_int = int(channel_id)
            if not await is_bot_admin_in_channel(channel_id_int):
                continue 

            if not await check_subscription(user_id, channel_id_int):
                unsubscribed_channels[channel_id] = channel

        if unsubscribed_channels:
            try:
                keyboard_markup = await generate_subscription_buttons(unsubscribed_channels)
                text = "<b>📢 <b>📢 Diqqat! Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling.\nKanallar ichidagi yolg'on va aldamchi habarlarga ishonmang!</b>:</b>"
                await message.answer(text, reply_markup=keyboard_markup, parse_mode="HTML")
            except Exception as e:
                print(f"❌ An error occurred: {e}")
            raise CancelHandler()
