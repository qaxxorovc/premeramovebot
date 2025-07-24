import random
from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loader import bot
from data.config import BOTUSERNAME
from filters.filters import IsAdmin, IsAdminFunksion
from database.manage_tables import get_mdd_channels, get_links

EMOJIS = ["🔥", "🌟", "💥", "🎉", "✨", "🚀", "😎", "🎈", "🍀", "💫"]


async def is_bot_admin_in_channel(channel_id: int) -> bool:
    try:
        member = await bot.get_chat_member(channel_id, bot.id)
        return member.status in ("administrator", "creator")
    except Exception as e:
        return False


async def check_subscription(user_id: int, channel_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception as e:
        print(
            f"[check_subscription] Cannot check user {user_id} in channel {channel_id}: {e}"
        )
        return False


async def generate_subscription_buttons(unsubscribed_channels: dict):
    channels_markup = InlineKeyboardMarkup(row_width=1)

    for channel_id, channel in unsubscribed_channels.items():
        try:
            channel_name = channel["name"]
            channel_username = channel["username"]
            channel_url = f"https://t.me/{channel_username}"
            emoji = random.choice(EMOJIS)

            button = InlineKeyboardButton(text=f"{channel_name} {emoji}", url=channel_url)
            channels_markup.add(button)
        except Exception as e:
            print(f"❌ Channel button creation failed: {e}")

    # --- Fake links ---
    fake_links = await get_links()
    print("🧪 fake_links:", fake_links)

    if fake_links and fake_links[0]:
        for i, link in enumerate(fake_links):
            try:
                link_name = link[1]
                link_url = link[2]
                emoji = random.choice(EMOJIS)

                button = InlineKeyboardButton(text=f"{link_name} {emoji}", url=link_url)
                channels_markup.add(button)
            except Exception as e:
                print(f"❌ Fake link failed: {e}")

    # --- Check button ---
    try:
        check_url = f"https://t.me/{BOTUSERNAME}?start=restart"
        check_button = InlineKeyboardButton(
            text="Tekshirish ♻️", url=check_url
        )
        channels_markup.add(check_button)
    except Exception as e:
        print(f"❌ Check button creation failed: {e}")

    return channels_markup


class SubscriptionCheckMiddleware(BaseMiddleware):
    async def on_process_update(self, update: types.Update, data: dict):
        message = update.message or (
            update.callback_query.message if update.callback_query else None
        )
        if not message:
            return

        user_id = message.from_user.id

        if update.message:
            if await IsAdmin()(update.message):
                return

        elif update.callback_query:
            if await IsAdminFunksion(update.callback_query.from_user.id):
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
                keyboard_markup = await generate_subscription_buttons(
                    unsubscribed_channels
                )
                
                text = (
"<b>📢 Diqqat!</b> "
"Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling.\n"
"<b>Kanallar ichidagi yolg'on va aldamchi habarlarga ishonmang!</b>"
)

                await message.answer(
                    text, reply_markup=keyboard_markup, parse_mode="HTML"
                )
            except Exception as e:
                print(f"❌ An error occurred: {e}")
            raise CancelHandler()
