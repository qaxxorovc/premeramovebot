from aiogram import types
from loader import dp,bot
from database.create_channels import connect_db
from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.inline.keyrboards import admin_menu, cancel_admin

@dp.callback_query_handler(lambda c: c.data.startswith("delete_serial_"))
async def confirm_serial_deletion(callback_query: types.CallbackQuery):
    serial_id = int(callback_query.data.split("_")[-1])
    
    conn, cur = await connect_db()
    cur.execute("SELECT title FROM serials WHERE id = ?;", (serial_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        await callback_query.message.answer("❌ Serial topilmadi yoki allaqachon o‘chirilgan.", reply_markup=admin_menu)
        await callback_query.answer()
        return

    title = row[0]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha, o‘chirilsin", callback_data=f"confirm_delete_{serial_id}"),
            InlineKeyboardButton(text="❌ Yo‘q, bekor qilish", callback_data="cancel_admin")
        ]
    ])

    await callback_query.message.answer(
        f"🗑️ <b>{title}</b> nomli serialni o‘chirmoqchimisiz?",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data.startswith("confirm_delete_"))
async def delete_serial(callback_query: types.CallbackQuery):
    serial_id = int(callback_query.data.split("_")[-1])

    conn, cur = await connect_db()
    try:
        cur.execute("DELETE FROM serials WHERE id = ?;", (serial_id,))
        conn.commit()
        await callback_query.message.answer("✅ Serial muvaffaqiyatli o‘chirildi.", reply_markup=admin_menu)
    except Exception as e:
        await callback_query.message.answer(f"❌ Xatolik: {e}", reply_markup=admin_menu)
    finally:
        conn.close()
        await callback_query.answer()


from aiogram import types
from aiogram.dispatcher import FSMContext
from loader import dp
from database.manage_tables import get_all_serials
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from handlers.admin.add_serial_episode import get_episodes_by_serial_id, RemoveEpisode

@dp.callback_query_handler(lambda c: c.data.startswith("removeep_serial:"), state=RemoveEpisode.waiting_for_serial_id)
async def ask_episode_for_removal(call: types.CallbackQuery, state: FSMContext):
    serial_id = int(call.data.split(":")[1])
    await state.update_data(serial_id=serial_id)

    episodes = await get_episodes_by_serial_id(serial_id)
    if not episodes:
        await call.message.edit_text("❌ Bu serialda qismlar topilmadi.", reply_markup=admin_menu)
        return

    markup = InlineKeyboardMarkup(row_width=2)
    for ep in episodes:
        ep_id, season, number = ep
        markup.insert(
            InlineKeyboardButton(
                text=f"{season}-fasl {number}-qism",
                callback_data=f"removeep_episode:{ep_id}"
            )
        )
    markup.insert(
        InlineKeyboardButton(
            text=f"❌ Bekor qilish",
            callback_data=f"cancel_admin"
        )
    )

    await call.message.edit_text("🎞 Qaysi qismni o‘chirmoqchisiz?", reply_markup=markup)
    await state.set_state(RemoveEpisode.waiting_for_episode_id)

from database.manage_tables import remove_episode_by_id

@dp.callback_query_handler(lambda c: c.data.startswith("removeep_episode:"), state=RemoveEpisode.waiting_for_episode_id)
async def remove_episode_confirm(call: types.CallbackQuery, state: FSMContext):
    episode_id = int(call.data.split(":")[1])
    await remove_episode_by_id(episode_id)
    await call.message.edit_text("✅ Qism muvaffaqiyatli o‘chirildi.", reply_markup=admin_menu)
    await state.finish()
