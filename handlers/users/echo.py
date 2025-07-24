from loader import dp
from aiogram import types
from database.manage_tables import (
    get_movie_by_id,
    get_user_premium_status,
    add_download,
    get_episode_by_id,
    get_serial_by_id,
)
from keyboards.inline.keyrboards import generate_episode_keyboard as episode_keyboard
from read_json import get_from_json


@dp.message_handler(lambda msg: msg.text.isdigit())
async def send_film_by_id(msg: types.Message):
    movie_id = int(msg.text)

    movie = await get_movie_by_id(movie_id)
    if movie:
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
            protect_content=True,
        )
        return

    episode = await get_episode_by_id(movie_id)
    if episode:
        bot_requires_premium = get_from_json("bot_requires_premium")

        if bot_requires_premium is True:
            is_premium = await get_user_premium_status(msg.from_user.id)
            if not is_premium:
                await msg.answer(
                    "❗️ Ushbu filmni ko‘rish uchun tarif sotib olishingiz kerak.\n"
                    "🛒 Tarif olish uchun /buy yoki menyudagi 'Tarif sotib olish' tugmasini bosing."
                )
                return

        episode_id, serial_id, season, episode_number, video_id = episode
        serial = await get_serial_by_id(serial_id)

        if not serial:
            await msg.answer("❌ Serial topilmadi.")
            return

        _, serial_title = serial

        caption = f"🎞 {serial_title}\n" f"📂 {season}-fasl {episode_number}-qism"

        await msg.answer_video(
            video=video_id,
            caption=caption,
            protect_content=True,
            reply_markup=await episode_keyboard(serial_id),
        )
        return

    # 3. Hech narsa topilmasa
    await msg.answer("❌ Bunday ID bilan film yoki qism topilmadi.")


@dp.callback_query_handler(lambda c: c.data.startswith("watch_episode:"))
async def watch_episode_handler(call: types.CallbackQuery):
    episode_id = int(call.data.split(":")[1])
    episode = await get_episode_by_id(episode_id)

    if episode:
        bot_requires_premium = get_from_json("bot_requires_premium")

        if bot_requires_premium is True:
            is_premium = await get_user_premium_status(call.message.from_user.id)
            if not is_premium:
                await call.message.answer(
                    "❗️ Ushbu filmni ko‘rish uchun tarif sotib olishingiz kerak.\n"
                    "🛒 Tarif olish uchun /buy yoki menyudagi 'Tarif sotib olish' tugmasini bosing."
                )
                return

        episode_id, serial_id, season, episode_number, video_id = episode
        serial = await get_serial_by_id(serial_id)

        if not serial:
            await call.message.answer("❌ Serial topilmadi.")
            return

        _, serial_title = serial

        caption = f"🎞 {serial_title}\n" f"📂 {season}-fasl {episode_number}-qism"
        try:

            await call.message.edit_media(
                video=video_id,
                caption=caption,
                protect_content=True,
                reply_markup=await episode_keyboard(serial_id),
            )
        except:

            await call.message.answer_video(
                video=video_id,
                caption=caption,
                protect_content=True,
                reply_markup=await episode_keyboard(serial_id),
            )
        return

    await call.message.answer("❌ Bunday ID bilan film yoki qism topilmadi.")
