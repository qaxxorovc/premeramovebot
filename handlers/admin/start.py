from aiogram import types
from loader import dp
from database.manage_tables import get_user_count
from filters.filters import IsAdmin
from keyboards.inline.keyrboards import admin_menu
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards.inline.keyrboards import manage_movies_keyboard, cancel_admin
from database.manage_tables import add_cash_to_user

from utils.adder_json import get_daily_users_count


class AddCashByAdmin(StatesGroup):
    waiting_sum = State()


@dp.message_handler(IsAdmin(), commands=["start"], state="*")
async def handle_start(message: types.Message, state: FSMContext):
    args = message.get_args()

    if args:
        user_id = args
        await state.update_data(target_user_id=int(user_id))
        await message.answer(
            f"✏️ Yangi qo‘shiladigan summani kiriting:", reply_markup=cancel_admin
        )
        await AddCashByAdmin.waiting_sum.set()
        return

    await message.answer(
        "👑 <b>Admin paneliga xush kelibsiz!</b>\n\n"
        "Bu yerda botni boshqarishingiz, xabarlar yuborishingiz, kanallarni sozlashingiz va statistikani ko‘rishingiz mumkin.\n"
        "Quyidan amal tanlang ⬇️",
        reply_markup=admin_menu,
        parse_mode="HTML",
    )
    await state.finish()


@dp.message_handler(state=AddCashByAdmin.waiting_sum)
async def receive_amount_from_admin(msg: types.Message, state: FSMContext):

    if not msg.text.isdigit():
        await msg.answer("❗️Faqat raqam kiriting.")
        return

    data = await state.get_data()
    target_user_id = data.get("target_user_id")

    if not target_user_id:
        await msg.answer("⚠️ Foydalanuvchi aniqlanmadi. /start orqali qayta urining.")
        await state.finish()
        return

    amount = int(msg.text)

    await add_cash_to_user(target_user_id, amount)
    await msg.bot.send_message(
        target_user_id, f"💰 Admin tomonidan hisobingizga {amount} so‘m qo‘shildi."
    )
    await msg.answer(
        f"✅ <code>{target_user_id}</code> foydalanuvchiga {amount} so‘m qo‘shildi."
    )
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == "manage_movies")
async def show_manage_movies(callback: types.CallbackQuery):
    await callback.message.edit_text(
        text="📽️ Film boshqaruv menyusi.\n\nQuyidagilardan birini tanlang:",
        reply_markup=manage_movies_keyboard,
    )
    await callback.answer()


@dp.callback_query_handler(IsAdmin(), lambda c: c.data == "cancel_admin", state="*")
async def cancel_admin_funktion(
    event: types.Message | types.CallbackQuery, state: FSMContext
):
    await state.finish()

    text = "✅ Barcha jarayonlar bekor qilindi. Siz admin paneliga qaytdingiz."

    if isinstance(event, types.Message):
        await event.answer(text, reply_markup=admin_menu)
    else:
        await event.message.edit_text(text, reply_markup=admin_menu)


@dp.callback_query_handler(lambda c: c.data == "admin_statistics", IsAdmin())
async def statistics_handler(call: types.CallbackQuery):
    user_count = await get_user_count()
    daily_count = get_daily_users_count()
    print(daily_count)

    text = (
        f"📊 <b>Bot statistikasi</b>\n\n"
        f"👤 Umumiy foydalanuvchilar soni: <b>{user_count}</b>\n"
        f"📅 Bugungi yangi foydalanuvchilar: <b>{daily_count}</b>\n\n"
        f"<i>ℹ️ Diqqat! Kunlik statistika har kuni soat 23:50 da avtomatik tarzda yangilanadi.\n"
        f"Iltimos, shu vaqtdan keyin aniqlik uchun qayta ko‘rib chiqing.</i>"
    )

    try:
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=admin_menu)
    except:
        await call.message.answer(text, parse_mode="HTML", reply_markup=admin_menu)
