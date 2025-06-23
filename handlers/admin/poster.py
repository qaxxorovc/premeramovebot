from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from loader import dp
from filters.filters import IsAdmin
from keyboards.inline.keyrboards import admin_menu
from database.manage_tables import get_all_user_ids


class AdminPost(StatesGroup):
    waiting_for_post = State()
    waiting_for_action = State()
    waiting_for_new_caption = State()
    waiting_for_rewrite = State()


@dp.callback_query_handler(lambda x: x.data == "admin_send_message", IsAdmin())
async def start_admin(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer(
        "📨 Foydalanuvchilarga yubormoqchi bo‘lgan to‘liq postni yuboring.\n\n"
        "Bu rasm, video, fayl, ovozli xabar, video eslatma yoki matnli media bo‘lishi mumkin."
    )
    await AdminPost.waiting_for_post.set()


@dp.message_handler(content_types=types.ContentType.ANY, state=AdminPost.waiting_for_post)
async def receive_post(message: types.Message, state: FSMContext):
    await state.update_data(post=message)
    await message.copy_to(chat_id=message.chat.id)

    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("✏️ Sarlavhani tahrirlash", callback_data="edit_caption"),
        types.InlineKeyboardButton("📝 Postni qayta yozish", callback_data="rewrite_post"),
        types.InlineKeyboardButton("📤 Hammaga yuborish", callback_data="send_to_all"),
        types.InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_post")
    )

    await message.answer("Post foydalanuvchilarga quyidagicha ko‘rinadi 👇", reply_markup=kb)
    await AdminPost.waiting_for_action.set()


@dp.callback_query_handler(lambda c: c.data == "edit_caption", state=AdminPost.waiting_for_action)
async def edit_caption(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("✏️ Yangi sarlavhani yuboring:")
    await AdminPost.waiting_for_new_caption.set()


@dp.message_handler(state=AdminPost.waiting_for_new_caption)
async def save_new_caption(message: types.Message, state: FSMContext):
    data = await state.get_data()
    old_msg: types.Message = data.get("post")

    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("✏️ Sarlavhani tahrirlash", callback_data="edit_caption"),
        types.InlineKeyboardButton("📝 Postni qayta yozish", callback_data="rewrite_post"),
        types.InlineKeyboardButton("📤 Hammaga yuborish", callback_data="send_to_all"),
        types.InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_post")
    )

    if old_msg.photo:
        await old_msg.bot.send_photo(chat_id=message.chat.id, photo=old_msg.photo[-1].file_id, caption=message.text)
    elif old_msg.video:
        await old_msg.bot.send_video(chat_id=message.chat.id, video=old_msg.video.file_id, caption=message.text)
    elif old_msg.document:
        await old_msg.bot.send_document(chat_id=message.chat.id, document=old_msg.document.file_id, caption=message.text)
    else:
        await message.answer("❌ Bu media turida sarlavha qo‘shib bo‘lmaydi.", reply_markup=kb)
        return

    await state.update_data(caption=message.text)
    await AdminPost.waiting_for_action.set()


@dp.callback_query_handler(lambda c: c.data == "rewrite_post", state=AdminPost.waiting_for_action)
async def rewrite_post(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("📝 Postni to‘liq qaytadan yuboring (matn yoki media):")
    await AdminPost.waiting_for_rewrite.set()


@dp.message_handler(content_types=types.ContentType.ANY, state=AdminPost.waiting_for_rewrite)
async def save_rewrite(message: types.Message, state: FSMContext):
    await state.update_data(post=message)
    await message.copy_to(chat_id=message.chat.id)
    await AdminPost.waiting_for_action.set()


@dp.callback_query_handler(lambda c: c.data == "cancel_post", state=AdminPost.waiting_for_action)
async def cancel_post(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await call.message.answer("❌ Post bekor qilindi.")
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == "send_to_all", state=AdminPost.waiting_for_action)
async def send_to_all(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg: types.Message = data.get("post")
    caption = data.get("caption")

    users = await get_all_user_ids()
    success, failed = 0, 0

    for user_id in users:
        try:
            if msg.text:
                await msg.bot.send_message(chat_id=user_id, text=msg.text)
            elif msg.photo:
                await msg.bot.send_photo(chat_id=user_id, photo=msg.photo[-1].file_id, caption=caption or msg.caption)
            elif msg.video:
                await msg.bot.send_video(chat_id=user_id, video=msg.video.file_id, caption=caption or msg.caption)
            elif msg.document:
                await msg.bot.send_document(chat_id=user_id, document=msg.document.file_id, caption=caption or msg.caption)
            elif msg.voice:
                await msg.bot.send_voice(chat_id=user_id, voice=msg.voice.file_id)
            elif msg.video_note:
                await msg.bot.send_video_note(chat_id=user_id, video_note=msg.video_note.file_id)
            else:
                continue
            success += 1
        except:
            failed += 1
            continue

    await call.message.answer(f"✅ {success} foydalanuvchiga yuborildi.\n❌ {failed} foydalanuvchiga yuborilmadi.", reply_markup=admin_menu)
    await state.finish()
