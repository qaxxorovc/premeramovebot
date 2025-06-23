from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup

from loader import dp, bot
from database.manage_tables import get_movie_by_id, connect_db
from filters.filters import IsAdmin

from keyboards.inline.keyrboards import cancel_admin, admin_menu

class EditMovieState(StatesGroup):
    waiting_for_id = State()
    choosing_field = State()
    entering_new_value = State()


# 🔘 O‘zgartirish menyusi
def edit_options_keyboard(movie_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton("✏️ Nomi", callback_data=f"edit_field:name:{movie_id}"),
            InlineKeyboardButton("🎥 Video", callback_data=f"edit_field:video:{movie_id}")
        ],
        [InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_admin")]
    ])


@dp.callback_query_handler(IsAdmin(),lambda c: c.data == "edit_film")
async def ask_movie_id(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("✏️ Qaysi filmni tahrirlashni xohlaysiz? Film ID raqamini yuboring:")
    await EditMovieState.waiting_for_id.set()
    await callback.answer()


@dp.message_handler(state=EditMovieState.waiting_for_id)
async def process_movie_id(msg: types.Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer("❗️ Faqat raqamli ID yuboring.")
        return

    movie_id = int(msg.text)
    movie = await get_movie_by_id(movie_id)
    if not movie:
        await msg.answer("<b>❌ Bunday ID bilan film topilmadi</b>\nTog'ri id kiriting.", reply_markup=cancel_admin, parse_mode="HTML")
        return

    await state.update_data(movie_id=movie_id)
    _, video, name, count = movie

    await msg.answer_video(
        video=video,
        caption=f"🎬 Nomi: <b>{name}</b>\n📥 Yuklab olingan: {count} marta\n\nNimani tahrirlaysiz?",
        parse_mode='HTML',
        reply_markup=edit_options_keyboard(movie_id)
    )
    await EditMovieState.choosing_field.set()


@dp.callback_query_handler(lambda c: c.data.startswith("edit_field:"), state=EditMovieState.choosing_field)
async def choose_field(callback: types.CallbackQuery, state: FSMContext):
    _, field, movie_id = callback.data.split(":")
    await state.update_data(field=field)
    await callback.message.answer(
        f"✏️ Yangi {'video' if field == 'video' else 'nom'} yuboring:",
        reply_markup=cancel_admin
    )
    await EditMovieState.entering_new_value.set()
    await callback.answer()


@dp.message_handler(state=EditMovieState.entering_new_value, content_types=types.ContentType.ANY)
async def update_field(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    movie_id = data['movie_id']
    field = data['field']

    # qiymatni aniqlash
    if field == 'video' and msg.video:
        new_value = msg.video.file_id
    elif field == 'name' and msg.text:
        new_value = msg.text
    else:
        await msg.reply("❗️ Noto‘g‘ri format. To‘g‘ri yuboring.",
        reply_markup=cancel_admin
        )
        return

    conn, cur = await connect_db()
    cur.execute(f"""
        update movies set movie_{field} = ?
        where movie_id = ?
    """, (new_value, movie_id))
    conn.commit()
    conn.close()

    await msg.answer(f"✅ Filmning {field} muvaffaqiyatli yangilandi.", reply_markup=admin_menu)
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == "cancel_admin", state='*')
async def cancel_edit(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback.message.answer("❌ Tahrirlash bekor qilindi.", reply_markup=admin_menu)
    await callback.answer()