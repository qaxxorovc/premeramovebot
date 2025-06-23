from aiogram import types
from loader import dp
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from read_json import get_from_json, change_from_json
from keyboards.inline.keyrboards import cancel_admin, admin_menu

class ChangeCardState(StatesGroup):
    waiting_for_card_number = State()
    waiting_for_card_owner = State()

class ChangeMoneyState(StatesGroup):
    waiting_for_new_price = State()

# --- Asosiy inline tugmalar ---
def premium_status_buttons():
    current_status = get_from_json("bot_requires_premium")
    status_text = "Bot Premium So'rash ( Yoqilgan ) ✅" if current_status else "Bot Premium So'rash ( O'chirilgan ) ❌"
    
    return types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text=status_text, callback_data="toggle_premium_status")],
        [types.InlineKeyboardButton(text="💰 Obuna narxini o‘zgartirish", callback_data="change_money_price")],
        [types.InlineKeyboardButton(text="💳 Carta raqam o'zgartirish", callback_data="change_card_number")],
        [types.InlineKeyboardButton(text="💳 Carta ega ismini o'zgartirish", callback_data="change_card_owner")],
        [types.InlineKeyboardButton(text="✴️ Obuna sotib olish help videosini sozlash", callback_data="set_video")],
        [types.InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_admin")]
    ])

# --- Callback: admin_manage_bot menyusi ---
@dp.callback_query_handler(lambda c: c.data == "admin_manage_bot")
async def manage_bot(callback: types.CallbackQuery):
    await callback.message.edit_text(
        text="⚙️ Bot sozlamalari menyusi:\n\nPremium so‘rash holatini va narxini boshqarishingiz mumkin:",
        reply_markup=premium_status_buttons()
    )
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == "change_card_number")
async def ask_card_number(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("💳 Yangi karta raqamini kiriting:", reply_markup=cancel_admin)
    await ChangeCardState.waiting_for_card_number.set()
    await callback.answer()

@dp.message_handler(state=ChangeCardState.waiting_for_card_number)
async def save_card_number(msg: types.Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer("❗️Faqat raqam kiriting.", reply_markup=cancel_admin)
        return

    change_from_json("card_number", int(msg.text))
    await msg.answer(f"✅ Karta raqami yangilandi: <code>{msg.text}</code>", parse_mode="HTML", reply_markup=admin_menu)
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == "change_card_owner")
async def ask_card_owner(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("👤 Yangi karta egasi ismini kiriting:", reply_markup=cancel_admin)
    await ChangeCardState.waiting_for_card_owner.set()
    await callback.answer()

@dp.message_handler(state=ChangeCardState.waiting_for_card_owner)
async def save_card_owner(msg: types.Message, state: FSMContext):
    full_name = msg.text
    change_from_json("card_owner", full_name)
    await msg.answer(f"✅ Karta egasi ismi yangilandi: <b>{full_name}</b>", parse_mode="HTML", reply_markup=admin_menu)
    await state.finish()


# --- Callback: Premium holatini o‘zgartirish ---
@dp.callback_query_handler(lambda c: c.data == "toggle_premium_status")
async def toggle_premium(callback: types.CallbackQuery):
    current_status = get_from_json("bot_requires_premium")
    new_status = not current_status
    change_from_json("bot_requires_premium", new_status)

    await callback.message.edit_text(
        text="✅ Premium so‘rash holati o‘zgartirildi:",
        reply_markup=premium_status_buttons()
    )
    await callback.answer("Holat o‘zgartirildi.")

# --- Callback: Obuna narxini o‘zgartirish ---
@dp.callback_query_handler(lambda c: c.data == "change_money_price")
async def ask_new_price(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("💰 Yangi obuna narxini so‘mda kiriting:", reply_markup=cancel_admin)
    await ChangeMoneyState.waiting_for_new_price.set()
    await callback.answer()

# --- State: Yangi narxni qabul qilish ---
@dp.message_handler(state=ChangeMoneyState.waiting_for_new_price)
async def save_new_price(msg: types.Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer("❗️Faqat raqam kiriting.", reply_markup=cancel_admin)
        return

    new_price = int(msg.text)
    change_from_json("bot_mouth_money", new_price)
    await msg.answer(f"✅ Yangi obuna narxi belgilandi: {new_price} so‘m", reply_markup=cancel_admin)
    await state.finish()
