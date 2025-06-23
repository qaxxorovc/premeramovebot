from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from loader import dp
from keyboards.inline.keyrboards import get_check_admin_buttons, cancel_user,sub_cc
from data.config import debug_group
from read_json import get_from_json, change_from_json
from database.manage_tables import get_user_data, update_user_premium
from datetime import datetime

class BuyStates(StatesGroup):
    amount = State()
    check = State()

from read_json import get_from_json

@dp.callback_query_handler(lambda x: x.data == "buy")
async def buy_start(call: types.CallbackQuery):
    user = await get_user_data(str(call.from_user.id))

    if not user:
        await call.message.answer("❌ Siz ro‘yxatdan o‘tmagansiz.")
        return

    if user['user_premium_status'] == "true":
        await call.message.answer("✅ Sizda allaqachon Premium obuna mavjud.")
        return

    cash = user['user_cash']
    sub_price = get_from_json("bot_mouth_money")

    text = f"""
<b>💎 1 oylik Premium obuna haqida:</b>

✅ Sizning hisobingiz: <b>{cash} so‘m🔥</b>  
✅ Obuna narxi: <b>{sub_price} so‘m</b>  
✅ Foyda: barcha filmlarni cheklovsiz yuklab olish
✅ Muddat: 30 kun
✅ Obuna avtomatik o‘chmaydi — muddat tugaganda xabarnoma bor

<b>💳 To‘lov uchun karta:</b>
🏦 <b>Karta raqami:</b> <code>{get_from_json("card_number")}</code>  
👤 <b>Egasi:</b> {get_from_json("card_owner")}

<i>To‘lovni amalga oshirgach, iltimos chekingizni yuboring.</i>

🔐 To‘lovingiz tekshirilgach, hisobingizga obuna qo‘shiladi.
"""
    await call.message.answer(text, reply_markup=sub_cc, parse_mode="HTML")

@dp.callback_query_handler(lambda x: x.data == "add_cash_money")
async def buy_start(call: types.CallbackQuery, state: FSMContext):
    helper_video = get_from_json("helper_video")


    if helper_video:  # agar video ID mavjud bo‘lsa
        text = f"<i>📹Videoda qanday qilib hisob to'ldirish ko'rsatilgan!</i>\n<b>💬 Ho‘sh, qancha tashlamoqchisiz?</b>"
        await call.message.answer_video(
            video=helper_video,
            caption=text,
            parse_mode="HTML",
            reply_markup=cancel_user
        )
    else:
        text = f"<b>💬 Ho‘sh, qancha tashlamoqchisiz?</b>"
        await call.message.answer(
            text,
            parse_mode="HTML",
            reply_markup=cancel_user
        )

    await BuyStates.amount.set()

@dp.callback_query_handler(lambda x: x.data == "buy_sub")
async def buy_subscription(callback: types.CallbackQuery):
    user_id = str(callback.from_user.id)
    user = await get_user_data(user_id)

    if not user:
        await callback.message.answer("❌ Foydalanuvchi topilmadi.")
        return

    user_cash = int(user['user_cash'])
    sub_price = int(get_from_json("bot_mouth_money"))

    if user_cash < sub_price:
        await callback.message.answer(
            f"❌ Obuna narxi {sub_price} so‘m. Sizda yetarli mablag‘ mavjud emas.\n"
            f"💰 Balans: {user_cash} so‘m"
        )
        return

    new_cash = user_cash - sub_price
    today = datetime.now().strftime("%d-%m-%Y")

    await update_user_premium(user_id=user_id, premium_status="true", sell_time=today, new_cash=new_cash)

    await callback.message.answer("✅ Tabriklaymiz! 1 oylik obunaga muvaffaqiyatli ulandingiz.")
    await callback.answer()


@dp.message_handler(commands="buy")
async def buy_start(msg: types.Message):
    text = f"""
<b>💎 1 oylik Premium obuna haqida:</b>

✅ Obuna narxi: <b>{get_from_json("bot_mouth_money")} so‘m</b>  
✅ Foyda: barcha filmlarni cheklovsiz yuklab olish
✅ Muddat: 30 kun
✅ Obuna avtomatik o‘chmaydi — muddat tugaganda xabarnoma bor

<b>💳 To‘lov uchun karta:</b>
🏦 <b>Karta raqami:</b> <code>{get_from_json("card_number")}</code>  
👤 <b>Egasi:</b> {get_from_json("card_owner")}

<i>To‘lovni amalga oshirgach, iltimos chekingizni yuboring.</i>

🔐 To‘lovingiz tekshirilgach, hisobingizga obuna qo‘shiladi.

<b>💬 Ho‘sh, qancha tashlamoqchisiz?</b>
"""    
    await msg.answer(text, reply_markup=sub_cc)
    await BuyStates.amount.set()

@dp.message_handler(state=BuyStates.amount)
async def get_amount(msg: types.Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer("❗️Faqat raqam kiriting.")
        return
    await state.update_data(amount=int(msg.text))
    await msg.answer("✅ Endi chekni yuboring (screenshot yoki rasm ko‘rinishida).")
    await BuyStates.check.set()

@dp.message_handler(content_types=types.ContentType.PHOTO, state=BuyStates.check)
async def get_check(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    amount = data.get("amount")
    user = msg.from_user

    caption = (
        f"💳 <b>Yangi to‘lov so‘rovi!</b>\n\n"
        f"👤 Foydalanuvchi: {user.full_name}\n"
        f"↔️ Username: @{user.username}\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"💰 So‘ralgan summa: <b>{amount} so‘m</b>"
    )

    await msg.bot.send_photo(
        chat_id=debug_group,
        photo=msg.photo[-1].file_id,
        caption=caption,
        reply_markup=get_check_admin_buttons(user_id=user.id, amount=amount),
        parse_mode="HTML"
    )

    await msg.answer("✅ Chek adminga yuborildi! Tez orada tekshiriladi.")
    await state.finish()
