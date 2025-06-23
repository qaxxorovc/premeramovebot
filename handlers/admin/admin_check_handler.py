from aiogram import types
from loader import dp
from database.manage_tables import add_cash_to_user
from keyboards.inline.keyrboards import get_check_admin_buttons
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

class CustomAmount(StatesGroup):
    waiting_amount = State()

@dp.callback_query_handler(lambda c: c.data.startswith("accept:"))
async def accept_payment(callback: types.CallbackQuery):
    _, user_id, amount = callback.data.split(":")
    user_id = int(user_id)
    amount = int(amount)

    await add_cash_to_user(user_id, amount)

    await callback.message.edit_caption(callback.message.caption + f"\n\n✅ Qabul qilindi: {amount} so‘m", reply_markup=None)
    await callback.bot.send_message(user_id, f"✅ To‘lovingiz tasdiqlandi. Hisobingizga {amount} so‘m qo‘shildi.")
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("reject:"))
async def reject_payment(callback: types.CallbackQuery):
    _, user_id = callback.data.split(":")
    user_id = int(user_id)

    await callback.message.edit_caption(callback.message.caption + f"\n\n❌ Rad etildi.", reply_markup=None)
    await callback.bot.send_message(user_id, "❌ To‘lovingiz rad etildi. Agar xatolik bo‘lsa, qayta urinib ko‘ring.")
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("custom:"))
async def ask_custom_amount(callback: types.CallbackQuery, state: FSMContext):
    _, user_id = callback.data.split(":")
    await state.update_data(user_id=int(user_id))
    await callback.message.edit_caption(callback.message.caption + "\n\n✏️ Admin boshqa summa kiritmoqda...")
    await callback.message.answer("✏️ Yangi qo‘shiladigan summani kiriting:")
    await CustomAmount.waiting_amount.set()

@dp.message_handler(state=CustomAmount.waiting_amount)
async def receive_custom_amount(msg: types.Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer("❗️Faqat raqam kiriting.")
        return
    amount = int(msg.text)
    data = await state.get_data()
    user_id = data.get("user_id")

    await add_cash_to_user(user_id, amount)
    await msg.bot.send_message(user_id, f"💰 Admin tomonidan hisobingizga {amount} so‘m qo‘shildi.")
    await msg.answer(f"✅ {user_id} foydalanuvchiga {amount} so‘m qo‘shildi.")
    await state.finish()
