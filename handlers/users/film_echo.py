from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from uuid import uuid4
from database.create_channels import connect_db
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loader import dp

@dp.inline_handler()
async def inline_movie_search(inline_query: InlineQuery):
    search_text = inline_query.query.lower()

    if not search_text:
        return 

    conn, cur = await connect_db()
    cur.execute("SELECT * FROM movies WHERE LOWER(movie_name) LIKE ?", (f"%{search_text}%",))
    results = cur.fetchall()
    conn.close()

    articles = []

    for row in results:
        movie_id, video_id, name, count = row

        articles.append(
            InlineQueryResultArticle(
                id=str(uuid4()),
                title=name.split("\n")[0][:64],
                description=name,
                input_message_content=InputTextMessageContent(
                    message_text=f"📽 {name}"
                ),
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton("🎬 Filmni olish", callback_data=f"get_movie:{movie_id}")
                ]])
            )
        )

    await inline_query.answer(articles, cache_time=1, is_personal=True)


from loader import dp, bot
from aiogram.types import CallbackQuery
from database.manage_tables import get_movie_by_id, get_user_premium_status, add_download
from read_json import get_from_json

@dp.callback_query_handler(lambda c: c.data.startswith("get_movie:"))
async def send_movie_video(callback_query: CallbackQuery):
    movie_id_str = callback_query.data.split(":")[1]

    if not movie_id_str.isdigit():
        await bot.send_message(callback_query.from_user.id, "❌ Noto‘g‘ri kino ID.")
        return

    movie_id = int(movie_id_str)
    movie = await get_movie_by_id(movie_id)

    if not movie:
        await bot.send_message(callback_query.from_user.id, "❌ Bunday ID bilan film topilmadi.")
        return

    bot_requires_premium = get_from_json("bot_requires_premium")

    if bot_requires_premium:
        is_premium = await get_user_premium_status(callback_query.from_user.id)
        if not is_premium:
            await bot.send_message(
                callback_query.from_user.id,
                "❗️ Ushbu filmni ko‘rish uchun tarif sotib olishingiz kerak.\n"
                "🛒 Tarif olish uchun /buy yoki menyudagi 'Tarif sotib olish' tugmasini bosing."
            )
            return

    await add_download(movie_id)
    _, video_id, name, count = movie

    await bot.send_video(
        chat_id=callback_query.from_user.id,
        video=video_id,
        caption=f"🎬 {name}\n📥 Yuklab olingan: {count} marta",
        protect_content=True
    )
