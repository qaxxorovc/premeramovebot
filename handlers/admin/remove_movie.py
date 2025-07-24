from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup

from loader import dp, bot
from database.manage_tables import get_movie_by_id, remove_movie
from filters.filters import IsAdmin


class RemoveFilmState(StatesGroup):
    waiting_for_id = State()


# --- Filmni o‘chirish menyusi ---
def confirm_remove_keyboard(film_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    "✅ Ha, o‘chirish", callback_data=f"confirm_remove:{film_id}"
                ),
                InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_admin"),
            ]
        ]
    )


@dp.callback_query_handler(IsAdmin(), lambda c: c.data == "remove_film")
async def ask_film_id(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📽️ O‘chirmoqchi bo‘lgan film ID raqamini yuboring:"
    )
    await RemoveFilmState.waiting_for_id.set()
    await callback.answer()


@dp.message_handler(state=RemoveFilmState.waiting_for_id)
async def process_film_id(msg: types.Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.reply("❗️ Iltimos, faqat raqamli ID yuboring.")
        return

    movie_id = int(msg.text)
    movie = await get_movie_by_id(movie_id)

    if not movie:
        await msg.answer("❌ Bunday ID bilan film topilmadi.")
        await state.finish()
        return

    await state.finish()
    movie_id, movie_video, movie_name, count = movie

    await msg.answer_video(
        video=movie_video,
        caption=f"📽️ Film: <b>{movie_name}</b>\n📥 Yuklab olingan: {count} marta\n\nFilmni o‘chirishni tasdiqlaysizmi?",
        parse_mode="HTML",
        reply_markup=confirm_remove_keyboard(movie_id),
    )


@dp.callback_query_handler(lambda c: c.data.startswith("confirm_remove:"))
async def confirm_deletion(callback: types.CallbackQuery):
    movie_id = int(callback.data.split(":")[1])
    await remove_movie(movie_id)
    await callback.message.edit_text("✅ Film muvaffaqiyatli o‘chirildi.")
    await callback.answer()


@dp.callback_query_handler(lambda c: c.data == "cancel_admin", state="*")
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await callback.message.edit_text("❌ Bekor qilindi.")
    await callback.answer()
