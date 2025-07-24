from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from keyboards.inline.keyrboards import cancel_admin, admin_menu
from database.manage_tables import (
    add_middleware_channel,
    remove_middleware_channel,
    get_all_channels,
)
from loader import dp, bot
from filters.filters import IsAdmin
from aiogram.dispatcher.filters.state import State, StatesGroup


class AddChannel(StatesGroup):
    waiting_for_channel_forward = State()


@dp.callback_query_handler(lambda c: c.data == "admin_manage_channels", IsAdmin())
async def manage_channels_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(text="➕ Kanal qo‘shish", callback_data="add_channel"),
        InlineKeyboardButton(
            text="➖ Kanalni o‘chirish", callback_data="remove_channel"
        ),
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="cancel_admin"),
    )

    await call.message.answer(
        "<b>📢 Kanal boshqaruvi menyusi</b>\n\n"
        "Iltimos, botga ulangan kanallarni boshqarish uchun amal tanlang:",
        reply_markup=markup,
        parse_mode="HTML",
    )


@dp.callback_query_handler(lambda c: c.data == "add_channel", IsAdmin())
async def add_channel_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer(
        "✅ Iltimos, qo‘shmoqchi bo‘lgan kanaldan biror xabarni oldinga yuboring (forward qiling).",
        reply_markup=cancel_admin,
    )
    await AddChannel.waiting_for_channel_forward.set()


@dp.message_handler(
    content_types=types.ContentType.ANY, state=AddChannel.waiting_for_channel_forward
)
async def handle_forwarded_channel(message: types.Message, state: FSMContext):
    if not message.forward_from_chat or message.forward_from_chat.type != "channel":
        await message.answer(
            "❌ Iltimos, faqatgina OMMAVIY kanaldan to‘g‘ridan-to‘g‘ri xabarni yuboring (forward)."
        )
        return

    channel = message.forward_from_chat
    channel_id = channel.id
    channel_title = channel.title
    channel_username = channel.username

    try:
        bot_member = await bot.get_chat_member(
            chat_id=channel_id, user_id=(await bot.me).id
        )
        if bot_member.status not in ("administrator", "creator"):
            raise Exception("Bot admin emas")
    except:
        await message.answer(
            "🚫 Bot ushbu kanalga administrator sifatida qo‘shilmagan. Iltimos, botni kanalga admin qilib qo‘shing va qayta urinib ko‘ring."
        )
        await state.finish()
        return

    await add_middleware_channel(
        name=channel_title,
        username=channel_username or "no-username",
        channel_id=channel_id,
    )

    await message.answer(
        f"✅ <b>{channel_title}</b> kanali muvaffaqiyatli qo‘shildi!",
        parse_mode="HTML",
        reply_markup=admin_menu,
    )
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == "remove_channel", IsAdmin())
async def remove_channel_handler(call: types.CallbackQuery):
    channels = await get_all_channels()

    if not channels:
        await call.message.answer("🚫 Hozircha hech qanday kanal qo‘shilmagan.")
        return

    text = "🗑 O‘chirmoqchi bo‘lgan kanalni tanlang:\n\n"
    kb = InlineKeyboardMarkup(row_width=1)

    for name, username, channel_id in channels:
        user_tag = f"@{username}" if username != "no-username" else f"ID: {channel_id}"
        text += f"🔹 <b>{name}</b> ({user_tag})\n"
        kb.add(
            InlineKeyboardButton(
                f"❌ O‘chirish — {name}", callback_data=f"delete_channel:{channel_id}"
            )
        )

    kb.add(InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_admin"))

    await call.message.answer(text, reply_markup=kb, parse_mode="HTML")


@dp.callback_query_handler(lambda c: c.data.startswith("delete_channel:"), IsAdmin())
async def delete_channel_handler(call: types.CallbackQuery):
    channel_id = call.data.split(":")[1]
    result = await remove_middleware_channel(channel_id)

    if result == True:
        await call.message.answer(
            "✅ Kanal muvaffaqiyatli o‘chirildi.", reply_markup=admin_menu
        )
        await call.message.delete()
    else:
        await call.message.answer(f"<code>{result}</code>", parse_mode="HTML")
