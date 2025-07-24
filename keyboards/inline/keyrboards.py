from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.config import admin_username, films_channel, BOTUSERNAME
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.manage_tables import get_episodes_by_serial_id
from collections import defaultdict


async def generate_episode_keyboard(serial_id: int) -> InlineKeyboardMarkup:
    episodes = await get_episodes_by_serial_id(serial_id)
    keyboard = InlineKeyboardMarkup(row_width=3)

    if not episodes:
        keyboard.add(
            InlineKeyboardButton(
                text="🎬 Hozircha epizodlar mavjud emas", callback_data="no_episodes"
            )
        )
        return keyboard

    grouped = defaultdict(list)
    for ep_id, season, ep_num in episodes:
        grouped[season].append((ep_id, ep_num))

    for season in sorted(grouped.keys()):
        if len(grouped) > 1:
            keyboard.add(
                InlineKeyboardButton(text=f"📁 {season}-FASL", callback_data="skip")
            )

        buttons = []
        for ep_id, ep_num in grouped[season]:
            text = f"{ep_num}-QISM"
            callback_data = f"watch_episode:{ep_id}"
            buttons.append(InlineKeyboardButton(text=text, callback_data=callback_data))

        for i in range(0, len(buttons), 3):
            keyboard.row(*buttons[i : i + 3])

    return keyboard


main_menu_for_users = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📽️ Film qidirish", url=f"https://t.me/{films_channel}"
            ),
            InlineKeyboardButton(text="🛒 Tarif sotib olish", callback_data="buy"),
        ],
        [
            InlineKeyboardButton(
                text="☎️ Admin bilan aloqa", url=f"https://t.me/{admin_username}"
            )
        ],
        [
            InlineKeyboardButton(
                text="📽️ Filmlarni nomi orqali qidirish",
                switch_inline_query_current_chat="",
            )
        ],
    ]
)

admin_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📨 Xabar yuborish", callback_data="admin_send_message"
            ),
            InlineKeyboardButton(
                text="📢 Kanallarni boshqarish", callback_data="admin_manage_channels"
            ),
        ],
        [InlineKeyboardButton(text="📽️ Filmlar bo'limi", callback_data="manage_movies")],
        [
            InlineKeyboardButton(
                text="📽️ Seriallar bo'limi", callback_data="serials_movies"
            )
        ],
        [
            InlineKeyboardButton(
                text="🤫 Soxta linklar", callback_data="add_fake_link_button"
            )
        ],
        [
            InlineKeyboardButton(
                text="🤖 Botni boshqarish", callback_data="admin_manage_bot"
            ),
            InlineKeyboardButton(
                text="📊 Statistika", callback_data="admin_statistics"
            ),
        ],
        [
            InlineKeyboardButton(
                text="👨‍💼 User malumotlarini olish", callback_data="get_user_data"
            )
        ],
    ]
)

fake_link_manager_keyrboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="⏬ Fake link qo'shish", callback_data="add_fake_link"
            ),
        ],
        [
            InlineKeyboardButton(
                text="🗑 Fake link o'chirish", callback_data="remove_fake_link"
            )
        ],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_admin")],
    ]
)

manage_movies_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📽️ Film qo'shish", callback_data="add_movie"),
        ],
        [
            InlineKeyboardButton(
                text="🗑️ Filmni o'chirish", callback_data="remove_film"
            ),
        ],
        [InlineKeyboardButton(text="✏️ Filmni tahrirlash", callback_data="edit_film")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_admin")],
    ]
)

serials_movies_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📽️ Serial yaratish", callback_data="create_serial"
            ),
        ],
        [
            InlineKeyboardButton(
                text="🗑️ Serialni o'chirish", callback_data="remove_serial"
            ),
        ],
        [
            InlineKeyboardButton(
                text="✏️ Serialga qism qo'shish", callback_data="add_episode"
            )
        ],
        [
            InlineKeyboardButton(
                text="🗑️ Serialdan qism O'chirish", callback_data="remove_episode"
            )
        ],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_admin")],
    ]
)


cancel_admin = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_admin")
)

sub_cc = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton(text="Obuna olish❕", callback_data="buy_sub"),
    InlineKeyboardButton(text="Hisob to'ldirish 💸", callback_data="add_cash_money"),
    InlineKeyboardButton(text="◀️ Orqaga", callback_data="cancel_user"),
)

cancel_user_back = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton(text="◀️ Orqaga", callback_data="cancel_user")
)

cancel_user = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_user")
)


def get_check_admin_buttons(user_id: int, amount: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    "✅ Qabul qilish", callback_data=f"accept:{user_id}:{amount}"
                ),
                InlineKeyboardButton("❌ Rad etish", callback_data=f"reject:{user_id}"),
            ],
            [
                InlineKeyboardButton(
                    "✏️ Boshqa summa qo‘shish",
                    url=f"https://t.me/{BOTUSERNAME}?start={user_id}",
                )
            ],
        ]
    )
