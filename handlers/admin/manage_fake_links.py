from aiogram import types
from loader import dp,bot
from keyboards.inline.keyrboards import cancel_admin, admin_menu, fake_link_manager_keyrboard
from database.manage_tables import add_link, remove_link, get_links
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class AddFakeLinkState(StatesGroup):
    waiting_for_name = State()
    waiting_for_url = State()


from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from loader import dp

@dp.callback_query_handler(lambda x: x.data == "add_fake_link_button")
async def start_adding_link(call: types.CallbackQuery):
    try:
        await call.message.edit_text("📝 Tugmalardan birini tanlang:", reply_markup=fake_link_manager_keyrboard)
    except:
        await call.message.answer("📝 Tugmalardan birini tanlang:", reply_markup=fake_link_manager_keyrboard)
        

@dp.callback_query_handler(lambda x: x.data == "add_fake_link")
async def start_adding_link(call: types.CallbackQuery):
    await call.message.answer("📝 Tugma uchun nom kiriting:", reply_markup=cancel_admin)
    await AddFakeLinkState.waiting_for_name.set()
    await call.answer()


@dp.message_handler(state=AddFakeLinkState.waiting_for_name)
async def get_link_name(message: types.Message, state: FSMContext):
    link_name = message.text.strip()
    await state.update_data(link_name=link_name)
    await message.answer("🔗 Linkni yuboring (https:// bilan boshlanishi kerak):")
    await AddFakeLinkState.waiting_for_url.set()


@dp.message_handler(state=AddFakeLinkState.waiting_for_url)
async def get_link_url(message: types.Message, state: FSMContext):
    link_url = message.text.strip()

    if not link_url.startswith("https://"):
        await message.answer("❌ Noto‘g‘ri format. Link https:// bilan boshlanishi kerak. Qayta urinib ko‘ring:")
        return

    data = await state.get_data()
    link_name = data['link_name']


    await add_link(link_name, link_url)

    await message.answer(f"✅ Link muvaffaqiyatli qabul qilindi:\n\n📌 <b>{link_name}</b>\n🔗 {link_url}", parse_mode="HTML", reply_markup=admin_menu)
    await state.finish()



@dp.callback_query_handler(lambda c: c.data == "remove_fake_link")
async def show_links_to_remove(call: types.CallbackQuery):
    fake_links = await get_links()

    if not fake_links:
        try:
            await call.message.edit_text("❌ Hech qanday fake link topilmadi.", reply_markup=admin_menu)
        except:
            await call.message.answer("❌ Hech qanday fake link topilmadi.", reply_markup=admin_menu)
        return

    keyboard = InlineKeyboardMarkup(row_width=1)
    for link_id, link_name, link_url in fake_links:
        keyboard.add(InlineKeyboardButton(
            text=f"🗑 {link_name}",
            callback_data=f"remove_fake_link_from_id:{link_id}"
        ))
    keyboard.add(InlineKeyboardButton(
        text=f"❌ Bekor qilish",
        callback_data=f"cancel_admin"
    ))


    await call.message.answer("🗑 Qaysi linkni o‘chirmoqchisiz?", reply_markup=keyboard)
    await call.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("remove_fake_link_from_id:"))
async def remove_selected_link(call: types.CallbackQuery):
    link_id = int(call.data.split(":")[1])

    await remove_link(link_id)

    await call.message.edit_text(f"✅ Link ID {link_id} muvaffaqiyatli o‘chirishga yuborildi.", reply_markup=admin_menu)
    await call.answer()
