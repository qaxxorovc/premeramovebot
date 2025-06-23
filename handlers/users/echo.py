from loader import dp
from aiogram import types
from database.manage_tables import get_movie_by_id, get_user_premium_status,add_download
from read_json import get_from_json


@dp.message_handler(lambda msg: msg.text.isdigit())
async def send_film_by_id(msg: types.Message):
    movie_id = int(msg.text)

    movie = await get_movie_by_id(movie_id)
    if not movie:
        await msg.answer("❌ Bunday ID bilan film topilmadi.")
        return
    await add_download(movie_id)
    bot_requires_premium = get_from_json("bot_requires_premium")

    if bot_requires_premium is True:
        is_premium = await get_user_premium_status(msg.from_user.id)
        if not is_premium:
            await msg.answer(
                "❗️ Ushbu filmni ko‘rish uchun tarif sotib olishingiz kerak.\n"
                "🛒 Tarif olish uchun /buy yoki menyudagi 'Tarif sotib olish' tugmasini bosing."
            )
            return

    _, video_id, name, count = movie
    await msg.answer_video(
        video=video_id,
        caption=f"🎬 {name}\n📥 Yuklab olingan: {count} marta",
        protect_content=True
    )
