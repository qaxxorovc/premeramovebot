from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import dp
from database.manage_tables import add_user

from keyboards.inline.keyrboards import main_menu_for_users
from aiogram.dispatcher.storage import FSMContext

from utils.adder_json import add_user_to_daily_count


@dp.message_handler(CommandStart(), state="*")
async def bot_start(message: types.Message, state: FSMContext):

    await add_user_to_daily_count(message.from_user.id)

    await message.answer(
        f"""<b>☺️ Assalomu alaykum {message.from_user.full_name}!</b>

Kerakli menyudan birini tanlang:""",
        parse_mode="HTML",
        reply_markup=main_menu_for_users,
    )
    await state.finish()
    await add_user(
        name=message.from_user.full_name,
        username=message.from_user.username,
        user_id=message.from_user.id,
    )


@dp.callback_query_handler(lambda c: c.data == "cancel_user", state="*")
async def cancel_user(call: types.CallbackQuery, state: FSMContext):
    await state.finish()

    text = "✅ Barcha jarayonlar bekor qilindi."

    try:
        await call.message.edit_text(text, reply_markup=main_menu_for_users)
    except:
        await call.message.answer(text, reply_markup=main_menu_for_users)
