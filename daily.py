from datetime import datetime
from loader import dp, bot
from database.manage_tables import connect_db


async def check_and_expire_subscriptions():
    conn, cur = await connect_db()
    cur.execute(
        "SELECT user_id, user_premium_sell_time FROM users WHERE user_premium_status = 'true'"
    )
    rows = cur.fetchall()

    for user_id, sell_time in rows:
        try:
            if sell_time == "00-00-0000":
                cur.execute(
                    """
                    UPDATE users 
                    SET user_premium_status = 'false'
                    WHERE user_id = ?
                """,
                    (str(user_id),),
                )
                continue

            delta_days = (
                datetime.now() - datetime.strptime(sell_time, "%d-%m-%Y")
            ).days
            if delta_days >= 30:
                cur.execute(
                    """
                    UPDATE users 
                    SET user_premium_status = 'false', 
                        user_premium_sell_time = '00-00-0000' 
                    WHERE user_id = ?
                """,
                    (str(user_id),),
                )
                try:
                    await bot.send_message(
                        user_id, "❌ Sizning Premium obunangiz muddati tugadi."
                    )
                except:
                    print("❌ Premium obunangiz muddati tugadi.")
        except Exception as e:
            print(f"[xatolik] foydalanuvchi {user_id} → {e}")

    conn.commit()
    conn.close()
