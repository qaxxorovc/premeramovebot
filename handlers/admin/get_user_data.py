from aiogram import types
from aiogram.dispatcher import FSMContext
from database.manage_tables import get_user_data
from loader import dp
from keyboards.inline.keyrboards import admin_menu, cancel_admin
from aiogram.dispatcher.filters.state import State, StatesGroup


class GetUserState(StatesGroup):
    waiting_for_user_id = State()


@dp.callback_query_handler(lambda c: c.data == "get_user_data")
async def ask_user_id(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "🔢 Foydalanuvchi ID raqamini kiriting:", reply_markup=cancel_admin
    )
    await GetUserState.waiting_for_user_id.set()
    await callback.answer()


@dp.message_handler(state=GetUserState.waiting_for_user_id)
async def show_user_info(msg: types.Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer("❗️ Iltimos, raqam kiriting.")
        return

    user_id = msg.text
    user = await get_user_data(user_id)

    if not user:
        await msg.answer("❌ Bunday foydalanuvchi topilmadi.")
    else:
        text = f"""
👤 <b>Foydalanuvchi Ma'lumotlari:</b>

🆔 ID: <code>{user['user_id']}</code>
📛 Ism: {user['user_name']}
🔗 Username: @{user['user_username']}
💰 Pul: {user['user_cash']} so‘m
💎 Premium: {'✅ Ha' if user['user_premium_status'] == 'true' else '❌ Yo‘q'}
🗓 Obuna vaqti: {user['user_premium_sell_time']}
        """
        await msg.answer(text, parse_mode="HTML", reply_markup=admin_menu)

    await state.finish()
