from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from loader import dp
from read_json import get_from_json, change_from_json
from keyboards.inline.keyrboards import cancel_admin, admin_menu
from filters.filters import IsAdmin


# --- Holat ---
class SetHelperVideoState(StatesGroup):
    waiting_for_video = State()


# --- Sozlama tugmasi ---
def helper_video_buttons():
    buttons = []

    current_video = get_from_json("helper_video")
    if current_video:
        buttons.append(
            [
                types.InlineKeyboardButton(
                    text="🗑 Videoni o‘chirish", callback_data="delete_helper_video"
                )
            ]
        )
    buttons.append(
        [
            types.InlineKeyboardButton(
                text="📥 Yangi video yuklash", callback_data="set_helper_video"
            )
        ]
    )
    buttons.append(
        [types.InlineKeyboardButton(text="◀️ Ortga", callback_data="cancel_admin")]
    )

    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


# --- Tugma orqali kirganda ---
@dp.callback_query_handler(IsAdmin(), lambda c: c.data == "set_video")
async def show_helper_video_options(call: types.CallbackQuery):
    await call.message.edit_text(
        text="🎬 Quyidan helper videoni sozlang:", reply_markup=helper_video_buttons()
    )
    await call.answer()


# --- Yangi video yuklash ---
@dp.callback_query_handler(IsAdmin(), lambda c: c.data == "set_helper_video")
async def ask_for_new_video(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(
        "📥 Iltimos, yangi helper videoni tashlang:", reply_markup=cancel_admin
    )
    await SetHelperVideoState.waiting_for_video.set()
    await call.answer()


@dp.message_handler(
    content_types=types.ContentType.VIDEO, state=SetHelperVideoState.waiting_for_video
)
async def save_new_helper_video(msg: types.Message, state: FSMContext):
    video_id = msg.video.file_id
    change_from_json("helper_video", video_id)
    await msg.answer("✅ Yangi helper video saqlandi.", reply_markup=admin_menu)
    await state.finish()


# --- Video o‘chirish ---
@dp.callback_query_handler(IsAdmin(), lambda c: c.data == "delete_helper_video")
async def delete_helper_video(call: types.CallbackQuery):
    change_from_json("helper_video", "")
    await call.message.edit_text(
        "🗑 Helper video o‘chirildi.", reply_markup=helper_video_buttons()
    )
    await call.answer("O‘chirildi.")
