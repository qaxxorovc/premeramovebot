from .create_channels import connect_db

async def add_user(name: str, username: str, user_id: int, premium_status: str = "false", cash: str = "0"):
    conn, cur = await connect_db()
    user_id = str(user_id)

    cur.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    exists = cur.fetchone()

    if not exists:
        cur.execute("""
            INSERT INTO users (user_name, user_username, user_premium_status, user_premium_sell_time, user_cash, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name.strip() if name else "",
            username.strip() if username else "",
            premium_status.lower(),
            "00-00-0000",
            cash,
            user_id
        ))
        conn.commit()

    conn.close()

async def remove_user(user_id: str):
    conn, cur = await connect_db()
    cur.execute("delete from users where user_id = ?", (user_id,))
    conn.commit()
    conn.close()


async def get_mdd_channels():
    conn, cur = await connect_db()
    cur.execute("SELECT Channel_Id, Channel_Name, Channel_Username FROM Middleware_Channels")
    rows = cur.fetchall()
    conn.close()
    if not rows:
        channels = None
    else:
        channels = {}
        for ch_id, name, username in rows:
            channels[ch_id] = {
                "name": name,
                "username": username
            }
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
        cur.execute("""
            INSERT INTO Middleware_Channels (Channel_Name, Channel_Username, Channel_Id)
            VALUES (?, ?, ?)
        """, (name, username, channel_id))
        conn.commit()

    conn.close()

async def remove_middleware_channel(channel_id: str):
    try:
        conn, cur = await connect_db()
        cur.execute("DELETE FROM Middleware_Channels WHERE Channel_Id = ?", (channel_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as Error:
        return {"error": str(Error)}

async def get_all_channels():
    conn, cur = await connect_db()
    cur.execute("SELECT Channel_Name, Channel_Username, Channel_Id FROM Middleware_Channels")
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
    conn, cur = await connect_db()

    # 1. Eng katta mavjud ID ni olish
    cur.execute("SELECT MAX(movie_id) FROM movies")
    last_id = cur.fetchone()[0]

    # 2. Yangi ID ni hosil qilish (agar yo'q bo'lsa, 100 dan boshlaydi)
    if last_id is None:
        movie_id = 100
    else:
        movie_id = last_id + random.choice([2, 3, 4])

    # 3. Bazaga qo'shish
    cur.execute("""
        INSERT INTO movies (movie_id, movie_video, movie_name, movie_download_count)
        VALUES (?, ?, ?, ?)
    """, (movie_id, movie_video, movie_name, 0))

    conn.commit()
    conn.close()

    return movie_id

async def get_movie_by_id(movie_id: int):
    conn, cur = await connect_db()
    cur.execute("""
        select movie_id, movie_video, movie_name, movie_download_count
        from movies where movie_id = ?
    """, (movie_id,))
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
    cur.execute("""
        update movies
        set movie_download_count = cast(movie_download_count as integer) + 1
        where movie_id = ?
    """, (movie_id,))
    conn.commit()
    conn.close()    


async def get_user_premium_status(user_id: int) -> bool:
    conn, cur = await connect_db()

    cur.execute("SELECT user_premium_status FROM users WHERE user_id = ?", (str(user_id),))
    result = cur.fetchone()

    conn.close()

    if result:
        if result[0].lower() == 'true':
            return True 
        return False

async def add_cash_to_user(user_id: int, amount: int):
    conn, cur = await connect_db()
    cur.execute("""
        UPDATE users
        SET user_cash = CAST(user_cash AS INTEGER) + ?
        WHERE user_id = ?
    """, (amount, str(user_id)))
    conn.commit()
    conn.close()

async def get_user_data(user_id: str):
    conn, cur = await connect_db()
    cur.execute("""
        SELECT user_name, user_username, user_premium_status, user_premium_sell_time, user_cash, user_id
        FROM users
        WHERE user_id = ?
    """, (str(user_id),))

    row = cur.fetchone()
    conn.close()

    if row:
        return {
            "user_name": row[0],
            "user_username": row[1],
            "user_premium_status": row[2],
            "user_premium_sell_time": row[3],
            "user_cash": row[4],
            "user_id": row[5]
        }
    return None    

async def update_user_premium(user_id: str, premium_status: str, sell_time: str, new_cash: int):
    conn, cur = await connect_db()
    cur.execute("""
        UPDATE users 
        SET user_premium_status = ?, 
            user_premium_sell_time = ?, 
            user_cash = ?
        WHERE user_id = ?
    """, (premium_status, sell_time, str(new_cash), str(user_id)))
    conn.commit()
    conn.close()    