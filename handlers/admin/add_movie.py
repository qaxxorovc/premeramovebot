import random
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup

from loader import dp, bot
from database.manage_tables import add_movie
from filters.filters import IsAdmin

from data.config import films_channel_id


# --- STATES ---
class AddMovieState(StatesGroup):
    video = State()
    name = State()


# --- CANCEL INLINE KEYBOARD ---
def cancel_keyboard():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_admin")
    )


# --- START COMMAND HANDLER ---
@dp.callback_query_handler(
    IsAdmin(), lambda c: c.data == "add_movie"
)  # ADMIN_ID ni real ID bilan almashtiring
async def add_movie_command(call: types.CallbackQuery):
    await call.message.answer(
        "🎬 Film videosini yuboring:", reply_markup=cancel_keyboard()
    )
    await AddMovieState.video.set()


# --- STEP 1: VIDEO ---
@dp.message_handler(content_types=types.ContentType.VIDEO, state=AddMovieState.video)
async def process_video(msg: types.Message, state: FSMContext):
    await state.update_data(movie_video=msg.video.file_id)
    await msg.answer("🎬 Endi film nomini yuboring:", reply_markup=cancel_keyboard())
    await AddMovieState.name.set()


@dp.message_handler(state=AddMovieState.name)
async def process_name(msg: types.Message, state: FSMContext):
    await state.update_data(movie_name=msg.text)
    data = await state.get_data()
    movie_video_id = data["movie_video"]

    try:
        movie_code = await add_movie(
            movie_name=data["movie_name"], movie_video=movie_video_id
        )

        await msg.answer(
            f"✅ Film muvaffaqiyatli qo‘shildi!\n<code>{movie_code}</code>",
            parse_mode="HTML",
        )

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🤖 Botga kirish",
                        url=f"https://t.me/{(await msg.bot.get_me()).username}",
                    )
                ]
            ]
        )

        caption = (
            f"🎬 Yangi film: <b>{data['movie_name']}</b>\n"
            f"📥 Yuklab olish kodi: <code>{movie_code}</code>\n\n"
            f"🕵️ Qiziqarli syujetli film, tavsiya qilamiz!"
        )

        await msg.bot.send_video(
            chat_id=films_channel_id,
            video=movie_video_id,
            caption=caption,
            reply_markup=keyboard,
            parse_mode="HTML",
        )

    except Exception as e:
        await msg.answer(f"❌ Xatolik: {e}")

    await state.finish()
