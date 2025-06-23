from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.config import admin_username, films_channel,BOTUSERNAME

main_menu_for_users = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="📽️ Film qidirish", url=f"https://t.me/{films_channel}"),
        InlineKeyboardButton(text="🛒 Tarif sotib olish", callback_data="buy"),
    ],
    [
        InlineKeyboardButton(text="☎️ Admin bilan aloqa", url=f"https://t.me/{admin_username}")
    ]
])

admin_menu = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="📨 Xabar yuborish", callback_data="admin_send_message"),
        InlineKeyboardButton(text="📢 Kanallarni boshqarish", callback_data="admin_manage_channels"),
    ],
    [
        InlineKeyboardButton(text="📽️ Filmlar bo'limi", callback_data="manage_movies")
    ],
    [
        InlineKeyboardButton(text="🤖 Botni boshqarish", callback_data="admin_manage_bot"),
        InlineKeyboardButton(text="📊 Statistika", callback_data="admin_statistics"),
    ],
    [
        InlineKeyboardButton(text="👨‍💼 User malumotlarini olish", callback_data="get_user_data")
    ]
])

manage_movies_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="📽️ Film qo'shish", callback_data="add_movie"),
    ],
    [
        InlineKeyboardButton(text="🗑️ Filmni o'chirish", callback_data="remove_film"),
    ],
    [
        InlineKeyboardButton(text="✏️ Filmni tahrirlash", callback_data="edit_film")
    ],
    [
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_admin")
    ]
])


cancel_admin = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_admin")
)

sub_cc = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton(text="Obuna olish❕", callback_data="buy_sub"),
    InlineKeyboardButton(text="Hisob to'ldirish 💸", callback_data="add_cash_money"),
    InlineKeyboardButton(text="Bekor qilish ❌", callback_data="cancel_user")
)

cancel_user = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_user")
)

def get_check_admin_buttons(user_id: int, amount: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton("✅ Qabul qilish", callback_data=f"accept:{user_id}:{amount}"),
            InlineKeyboardButton("❌ Rad etish", callback_data=f"reject:{user_id}")
        ],
        [
            InlineKeyboardButton(
                "✏️ Boshqa summa qo‘shish",
                url=f"https://t.me/{BOTUSERNAME}?start={user_id}"
            )
        ]
    ])