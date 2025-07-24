from .create_channels import connect_db
import random


async def generate_unique_media_id():
    conn, cur = await connect_db()
    try:
        existing_ids = set()

        # Movies ID
        cur.execute("SELECT movie_id FROM movies")
        existing_ids.update([row[0] for row in cur.fetchall()])

        # Episodes ID
        cur.execute("SELECT id FROM episodes")
        existing_ids.update([row[0] for row in cur.fetchall()])

        # 100–9999 oralig‘ida bo‘sh ID topamiz
        for _ in range(100):  # maksimal 100 ta urinish
            random_id = random.randint(100, 9999)
            if random_id not in existing_ids:
                return random_id

        raise Exception("❌ Bo‘sh ID topilmadi. Harakat soni tugadi.")

    finally:
        conn.close()


async def generate_unique_episode_id():
    conn, cur = await connect_db()

    try:
        existing_ids = set()

        # movies va episodes dan mavjud IDlarni olib qo‘shamiz
        cur.execute("SELECT movie_id FROM movies")
        existing_ids.update([row[0] for row in cur.fetchall()])

        cur.execute("SELECT id FROM episodes")
        existing_ids.update([row[0] for row in cur.fetchall()])

        # Random ID generatsiya qilish (cheksiz emas, 100 dan 9999 gacha)
        for _ in range(100):  # maksimal 100 urinish
            random_id = random.randint(100, 9999)
            if random_id not in existing_ids:
                return random_id

        raise Exception("❌ Bo‘sh ID topilmadi, qayta urinib ko‘ring.")

    finally:
        conn.close()


async def add_user(
    name: str,
    username: str,
    user_id: int,
    premium_status: str = "false",
    cash: str = "0",
):
    conn, cur = await connect_db()
    user_id = str(user_id)

    cur.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    exists = cur.fetchone()

    if not exists:
        cur.execute(
            """
            INSERT INTO users (user_name, user_username, user_premium_status, user_premium_sell_time, user_cash, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                name.strip() if name else "",
                username.strip() if username else "",
                premium_status.lower(),
                "00-00-0000",
                cash,
                user_id,
            ),
        )
        conn.commit()

    conn.close()


async def remove_user(user_id: str):
    conn, cur = await connect_db()
    cur.execute("delete from users where user_id = ?", (user_id,))
    conn.commit()
    conn.close()


async def get_mdd_channels():
    conn, cur = await connect_db()
    cur.execute(
        "SELECT Channel_Id, Channel_Name, Channel_Username FROM Middleware_Channels"
    )
    rows = cur.fetchall()
    conn.close()
    if not rows:
        channels = None
    else:
        channels = {}
        for ch_id, name, username in rows:
            channels[ch_id] = {"name": name, "username": username}
    return channels


async def get_all_user_ids() -> list[str]:
    conn, cur = await connect_db()
    cur.execute("SELECT User_Id FROM Users")
    rows = cur.fetchall()
    conn.close()
    return [row[0] for row in rows]


async def add_middleware_channel(name: str, username: str, channel_id: str):
    conn, cur = await connect_db()

    cur.execute("SELECT 1 FROM Middleware_Channels WHERE Channel_Id = ?", (channel_id,))
    exists = cur.fetchone()

    if not exists:
        cur.execute(
            """
            INSERT INTO Middleware_Channels (Channel_Name, Channel_Username, Channel_Id)
            VALUES (?, ?, ?)
        """,
            (name, username, channel_id),
        )
        conn.commit()

    conn.close()


async def remove_middleware_channel(channel_id: str):
    try:
        conn, cur = await connect_db()
        cur.execute(
            "DELETE FROM Middleware_Channels WHERE Channel_Id = ?", (channel_id,)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as Error:
        return {"error": str(Error)}


async def get_all_channels():
    conn, cur = await connect_db()
    cur.execute(
        "SELECT Channel_Name, Channel_Username, Channel_Id FROM Middleware_Channels"
    )
    rows = cur.fetchall()
    conn.close()
    return rows


async def get_user_count():
    conn, cur = await connect_db()
    cur.execute("SELECT COUNT(*) FROM Users")
    count = cur.fetchone()[0]
    conn.close()
    return count


async def get_user_count():
    conn, cur = await connect_db()
    cur.execute("SELECT COUNT(*) FROM Users")
    count = cur.fetchone()[0]
    conn.close()
    return count


import random


async def add_movie(movie_name: str, movie_video: str):
    """
    Yangi filmni bazaga qo‘shadi, takrorlanmas ID bilan.
    """
    conn, cur = await connect_db()
    try:
        movie_id = await generate_unique_media_id()

        cur.execute(
            """
            INSERT INTO movies (movie_id, movie_video, movie_name, movie_download_count)
            VALUES (?, ?, ?, 0);
        """,
            (movie_id, movie_video.strip(), movie_name.strip()),
        )

        conn.commit()
        print(f"✅ Film muvaffaqiyatli qo‘shildi. ID = {movie_id}")
        return movie_id

    except Exception as e:
        print(f"❌ Film qo‘shishda xatolik: {e}")
        return None

    finally:
        conn.close()


async def get_movie_by_id(movie_id: int):
    conn, cur = await connect_db()
    cur.execute(
        """
        select movie_id, movie_video, movie_name, movie_download_count
        from movies where movie_id = ?
    """,
        (movie_id,),
    )
    result = cur.fetchone()
    conn.close()
    return result


async def remove_movie(movie_id: int):
    conn, cur = await connect_db()
    cur.execute("delete from movies where movie_id = ?", (movie_id,))
    conn.commit()
    conn.close()


async def add_download(movie_id: int):
    conn, cur = await connect_db()
    cur.execute(
        """
        update movies
        set movie_download_count = cast(movie_download_count as integer) + 1
        where movie_id = ?
    """,
        (movie_id,),
    )
    conn.commit()
    conn.close()


async def get_user_premium_status(user_id: int) -> bool:
    conn, cur = await connect_db()

    cur.execute(
        "SELECT user_premium_status FROM users WHERE user_id = ?", (str(user_id),)
    )
    result = cur.fetchone()

    conn.close()

    if result:
        if result[0].lower() == "true":
            return True
        return False


async def add_cash_to_user(user_id: int, amount: int):
    conn, cur = await connect_db()
    cur.execute(
        """
        UPDATE users
        SET user_cash = CAST(user_cash AS INTEGER) + ?
        WHERE user_id = ?
    """,
        (amount, str(user_id)),
    )
    conn.commit()
    conn.close()


async def get_user_data(user_id: str):
    conn, cur = await connect_db()
    cur.execute(
        """
        SELECT user_name, user_username, user_premium_status, user_premium_sell_time, user_cash, user_id
        FROM users
        WHERE user_id = ?
    """,
        (str(user_id),),
    )

    row = cur.fetchone()
    conn.close()

    if row:
        return {
            "user_name": row[0],
            "user_username": row[1],
            "user_premium_status": row[2],
            "user_premium_sell_time": row[3],
            "user_cash": row[4],
            "user_id": row[5],
        }
    return None


async def update_user_premium(
    user_id: str, premium_status: str, sell_time: str, new_cash: int
):
    conn, cur = await connect_db()
    cur.execute(
        """
        UPDATE users 
        SET user_premium_status = ?, 
            user_premium_sell_time = ?, 
            user_cash = ?
        WHERE user_id = ?
    """,
        (premium_status, sell_time, str(new_cash), str(user_id)),
    )
    conn.commit()
    conn.close()


import random


async def add_link(link_name: str, link_url: str):
    conn, cur = await connect_db()

    while True:
        link_id = random.randint(100000, 999999)
        cur.execute("SELECT 1 FROM fake_links WHERE id = ?", (link_id,))
        exists = cur.fetchone()
        if not exists:
            break

    cur.execute(
        "INSERT INTO fake_links (id, link_name, link_url) VALUES (?, ?, ?)",
        (link_id, link_name, link_url),
    )
    conn.commit()
    conn.close()


async def remove_link(link_id: int):
    conn, cur = await connect_db()
    cur.execute("DELETE FROM fake_links WHERE id = ?", (link_id,))
    conn.commit()
    conn.close()


async def get_links():
    conn, cur = await connect_db()
    cur.execute("SELECT * FROM fake_links")
    rows = cur.fetchall()
    conn.close()
    return rows


async def add_serial(title: str):
    conn, cur = await connect_db()
    try:
        cur.execute("INSERT INTO serials (title) VALUES (?);", (title,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Serial qo‘shishda xatolik: {e}")
        conn.close()
        return False


async def add_episode(serial_id: int, season: int, episode_number: int, video: str):
    conn, cur = await connect_db()
    try:
        episode_id = await generate_unique_episode_id()

        cur.execute(
            """
            INSERT INTO episodes (id, serial_id, video, season, episode_number)
            VALUES (?, ?, ?, ?, ?);
        """,
            (episode_id, serial_id, video.strip(), season, episode_number),
        )

        conn.commit()
        return episode_id
    except Exception as e:
        print(f"❌ Epizod qo‘shishda xatolik: {e}")
    finally:
        conn.close()


async def remove_serial_by_id(serial_id: int):
    conn, cur = await connect_db()
    try:

        cur.execute("DELETE FROM episodes WHERE serial_id = ?;", (serial_id,))

        cur.execute("DELETE FROM serials WHERE id = ?;", (serial_id,))
        conn.commit()
    except Exception as e:
        print(f"Serial o‘chirishda xatolik: {e}")
    finally:
        conn.close()


async def remove_episode_by_id(episode_id: int):
    conn, cur = await connect_db()
    try:
        cur.execute("SELECT id FROM episodes WHERE id = ?;", (episode_id,))
        if not cur.fetchone():
            print("Bunday ID bilan epizod topilmadi.")
            return

        cur.execute("DELETE FROM episodes WHERE id = ?;", (episode_id,))
        conn.commit()
        print(f"{episode_id=} epizod muvaffaqiyatli o‘chirildi.")
    except Exception as e:
        print(f"Epizodni o‘chirishda xatolik: {e}")
    finally:
        conn.close()


async def get_serials():
    conn, cur = await connect_db()
    try:
        cur.execute("SELECT id, title FROM serials ORDER BY id;")
        rows = cur.fetchall()
        return rows
    except Exception as e:
        print(f"Seriallarni olishda xatolik: {e}")
        return []
    finally:
        conn.close()


async def get_episodes_by_serial_id(serial_id: int):
    conn, cur = await connect_db()
    try:
        cur.execute(
            """
            SELECT id, season, episode_number 
            FROM episodes 
            WHERE serial_id = ? 
            ORDER BY season, episode_number;
        """,
            (serial_id,),
        )
        rows = cur.fetchall()
        return rows
    except Exception as e:
        print(f"Epizodlarni olishda xatolik: {e}")
        return []
    finally:
        conn.close()


async def get_episode_by_id(episode_id: int):
    conn, cur = await connect_db()
    try:
        cur.execute(
            """
            SELECT id, serial_id, season, episode_number, video
            FROM episodes
            WHERE id = ?;
        """,
            (episode_id,),
        )
        row = cur.fetchone()
        return row
    except Exception as e:
        print(f"❌ Epizod topishda xatolik: {e}")
        return None
    finally:
        conn.close()


async def get_serial_by_id(serial_id: int):
    conn, cur = await connect_db()
    cur.execute("SELECT * FROM serials WHERE id = ?", (serial_id,))
    return cur.fetchone()


async def get_all_serials():
    conn, cur = await connect_db()
    try:
        cur.execute("SELECT id, title FROM serials")
        return cur.fetchall()
    finally:
        conn.close()


async def get_serial_title_by_id(serial_id: int) -> str | None:
    conn, cur = await connect_db()
    try:
        cur.execute("SELECT title FROM serials WHERE id = ?", (serial_id,))
        row = cur.fetchone()
        if row:
            return row[0]  # faqat title
        return None
    finally:
        conn.close()
