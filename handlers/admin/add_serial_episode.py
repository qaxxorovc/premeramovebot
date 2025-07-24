from aiogram import types
from aiogram.types import CallbackQuery
from aiogram.dispatcher import Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import dp, bot
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from database.manage_tables import (
    add_serial,
    add_episode,
    get_serials,
    get_episodes_by_serial_id,
    get_all_serials,
    get_serial_by_id,
    get_serial_title_by_id,
)
from keyboards.inline.keyrboards import (
    admin_menu,
    cancel_admin,
    serials_movies_keyboard,
)
from data.config import films_channel_id


class RemoveEpisode(StatesGroup):
    waiting_for_serial_id = State()
    waiting_for_episode_id = State()


class CreateSerial(StatesGroup):
    waiting_for_title = State()


class AddEpisode(StatesGroup):
    serial_id = State()
    video = State()
    episode = State()
    season = State()


SERIALS_PER_PAGE = 8


# ========================================================
async def get_serial_buttons(page: int = 0):
    rows = await get_serials()
    total = len(rows)
    start = page * SERIALS_PER_PAGE
    end = start + SERIALS_PER_PAGE

    current_page_serials = rows[start:end]

    buttons = []

    for serial_id, title in current_page_serials:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"🗑️ {title}", callback_data=f"delete_serial_{serial_id}"
                )
            ]
        )

    nav_buttons = []

    if end < total:
        nav_buttons.append(
            InlineKeyboardButton(
                text="➡️ Keyingisi", callback_data=f"serial_page_{page + 1}"
            )
        )

    if page > 0:
        nav_buttons.insert(
            0,
            InlineKeyboardButton(
                text="⬅️ Oldingisi", callback_data=f"serial_page_{page - 1}"
            ),
        )

    nav_buttons.append(
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_admin")
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons + [nav_buttons])


async def get_serial_buttons_for_episode(page: int = 0):
    rows = await get_serials()
    total = len(rows)
    start = page * SERIALS_PER_PAGE
    end = start + SERIALS_PER_PAGE

    current_page_serials = rows[start:end]

    buttons = []

    for serial_id, title in current_page_serials:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"💠 {title}",
                    callback_data=f"get_serial_buttons_for_episode:{serial_id}",
                )
            ]
        )

    nav_buttons = []

    if end < total:
        nav_buttons.append(
            InlineKeyboardButton(
                text="➡️ Keyingisi", callback_data=f"serial_page2_{page + 1}"
            )
        )

    if page > 0:
        nav_buttons.insert(
            0,
            InlineKeyboardButton(
                text="⬅️ Oldingisi", callback_data=f"serial_page2_{page - 1}"
            ),
        )

    nav_buttons.append(
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_admin")
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons + [nav_buttons])


# ==================================================


@dp.callback_query_handler(lambda c: c.data == "serials_movies")
async def handle_serials_menu(callback_query: CallbackQuery):
    try:
        await callback_query.message.edit_text(
            "📽️ Nima qilishni hohlaysiz?", reply_markup=serials_movies_keyboard
        )
    except:
        await callback_query.message.answer(
            "📽️ Nima qilishni hohlaysiz?", reply_markup=serials_movies_keyboard
        )
    await callback_query.answer()


@dp.callback_query_handler(
    lambda c: c.data
    in [
        "create_serial",
        "remove_serial",
        "add_episode",
        "remove_episode",
        "cancel_admin",
    ]
)
async def handle_serials_menu(callback_query: CallbackQuery):
    data = callback_query.data

    if data == "create_serial":
        await callback_query.message.answer(
            "📽️ Iltimos, serial nomini yuboring:", reply_markup=cancel_admin
        )
        await CreateSerial.waiting_for_title.set()
        await callback_query.answer()

    elif data == "remove_serial":
        keyboard = await get_serial_buttons(page=0)
        await callback_query.message.answer(
            "🗑️ O‘chirmoqchi bo‘lgan serialni tanlang:", reply_markup=keyboard
        )
        await callback_query.answer()

    elif data == "add_episode":
        keyboard = await get_serial_buttons_for_episode(page=0)
        await callback_query.message.answer(
            "✏️ Qaysi serialga qism qo‘shmoqchisiz?", reply_markup=keyboard
        )
        await AddEpisode.serial_id.set()
        await callback_query.answer()

    elif data == "remove_episode":
        print("RUNNING.")
        serials = await get_all_serials()
        if not serials:
            await callback_query.answer("❌ Seriallar topilmadi.")
            return

        markup = InlineKeyboardMarkup(row_width=1)
        for serial in serials:
            serial_id, title = serial
            markup.insert(
                InlineKeyboardButton(
                    text=title, callback_data=f"removeep_serial:{serial_id}"
                )
            )

        await callback_query.message.edit_text(
            "📺 Qaysi serialdan qism o‘chirmoqchisiz?", reply_markup=markup
        )
        await RemoveEpisode.waiting_for_serial_id.set()

    from database.manage_tables import get_episodes_by_serial_id

    await callback_query.answer()


@dp.message_handler(state=CreateSerial.waiting_for_title)
async def receive_serial_title(message: types.Message, state: FSMContext):
    title = message.text.strip()

    success = await add_serial(title)

    if success:
        await message.answer(
            f'✅ Serial "{title}" muvaffaqiyatli yaratildi.', reply_markup=admin_menu
        )
    else:
        await message.answer(
            f'⚠️ Serial "{title}" allaqachon mavjud yoki xatolik yuz berdi.',
            reply_markup=admin_menu,
        )

    await state.finish()


@dp.callback_query_handler(lambda c: c.data.startswith("serial_page_"), state="*")
async def handle_serial_pagination(callback_query: types.CallbackQuery):
    page = int(callback_query.data.split("_")[-1])
    keyboard = await get_serial_buttons(page=page)
    await callback_query.message.edit_reply_markup(reply_markup=keyboard)
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data.startswith("serial_page2_"), state="*")
async def handle_serial_pagination(callback_query: types.CallbackQuery):
    try:
        page = int(callback_query.data.split("_")[-1])

        keyboard = await get_serial_buttons_for_episode(page=page)

        await callback_query.message.edit_reply_markup(reply_markup=keyboard)

        await callback_query.answer()

    except Exception as e:
        print(f"[handle_serial_pagination] Xatolik: {e}")
        await callback_query.answer("❌ Sahifani yuklashda xatolik!", show_alert=True)


@dp.callback_query_handler(
    lambda c: c.data.startswith("get_serial_buttons_for_episode:"),
    state=AddEpisode.serial_id,
)
async def handle_serial_selection(
    callback_query: types.CallbackQuery, state: FSMContext
):
    try:
        serial_id = int(callback_query.data.split(":")[1])
        await state.update_data(serial_id=serial_id)

        await callback_query.message.answer(
            "🎬 Iltimos, serial videosini jo'nating:", reply_markup=cancel_admin
        )
        await AddEpisode.video.set()
        await callback_query.answer()
    except Exception as e:
        await callback_query.message.answer(f"❌ Xatolik yuz berdi: {e}")


@dp.message_handler(state=AddEpisode.video, content_types=types.ContentType.VIDEO)
async def receive_video(message: types.Message, state: FSMContext):
    """
    Video faylni qabul qiladi.
    """
    video_id = message.video.file_id
    await state.update_data(video=video_id)

    await message.answer(
        "🎯 Iltimos, nechanchi **qism**ligini kiriting (raqamda):",
        reply_markup=cancel_admin,
    )
    await AddEpisode.episode.set()


@dp.message_handler(state=AddEpisode.episode)
async def receive_episode(message: types.Message, state: FSMContext):
    """
    Epizod raqamini qabul qiladi.
    """
    try:
        episode = int(message.text.strip())
        await state.update_data(episode=episode)

        await message.answer(
            "📅 Endi nechanchi **sezon**ligini kiriting (raqamda):",
            reply_markup=cancel_admin,
        )
        await AddEpisode.season.set()
    except ValueError:
        await message.answer(
            "❗️ Iltimos, faqat raqam kiriting. Masalan: `1`, `2`, `3`",
            reply_markup=cancel_admin,
        )


@dp.message_handler(state=AddEpisode.season)
async def receive_season(message: types.Message, state: FSMContext):
    """
    Sezon raqamini qabul qiladi va ma'lumotlarni DBga yozadi.
    """
    try:
        season = int(message.text.strip())
        await state.update_data(season=season)

        data = await state.get_data()
        serial_id = data.get("serial_id")
        video = data.get("video")
        episode = data.get("episode")

        serial_title = await get_serial_title_by_id(serial_id)

        code = await add_episode(
            serial_id=serial_id, season=season, episode_number=episode, video=video
        )

        await message.bot.send_video(
            chat_id=films_channel_id,
            video=video,
            caption=f"{serial_title} - serial\n{episode} - qism\n{season} - sezon\nKod: {code}\nQo'shildi!",
            parse_mode="HTML",
        )

        await message.answer(
            "✅ Epizod muvaffaqiyatli qo‘shildi.", reply_markup=admin_menu
        )
        await state.finish()

    except ValueError:
        await message.answer(
            "❗️ Iltimos, faqat raqam kiriting. Masalan: `1`, `2`, `3`",
            reply_markup=cancel_admin,
        )
    except Exception as e:
        await message.answer(f"❌ Epizodni saqlashda xatolik yuz berdi: {e}")
        await state.finish()
