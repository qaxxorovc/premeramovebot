import sqlite3 as sq

# await create_admins_table()
# await create_channels_table()
# await create_users_table()

# async def connect_db():
#     conn = sq.connect('/home/LOCATE/BOTFOLDERNAME/database.db')
#     cur = conn.cursor()
#     return conn, cur


async def connect_db():
    conn = sq.connect("database.db")
    cur = conn.cursor()
    return conn, cur


async def bot_users():
    conn, cur = await connect_db()
    cur.execute(
        """
        create table if not exists users 
        (
            user_name varchar(255),
            user_username varchar(255) not null,
            user_premium_status varchar(255) not null,
            user_cash varchar(255) not null,
            user_premium_sell_time varchar(255) not null,
            user_id varchar(255) not null
        )        
    """
    )
    conn.commit()
    conn.close()


async def movies_data():
    conn, cur = await connect_db()
    cur.execute(
        """
        create table if not exists movies 
        (
            movie_id integer primary key,
            movie_video text,
            movie_name varchar(255),
            movie_download_count integer not null
        )
    """
    )
    conn.commit()
    conn.close()


async def serials():
    conn, cur = await connect_db()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS serials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL UNIQUE
        );
    """
    )
    conn.commit()
    conn.close()


async def episodes():
    conn, cur = await connect_db()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY,
            serial_id INTEGER NOT NULL,
            video TEXT,
            season INTEGER NOT NULL,
            episode_number INTEGER NOT NULL,
            
            FOREIGN KEY (serial_id) REFERENCES serials(id) ON DELETE CASCADE,
            
            UNIQUE(serial_id, season, episode_number)
        );
    """
    )
    conn.commit()
    conn.close()


async def fake_links():
    conn, cur = await connect_db()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS fake_links 
        (
            id INTEGER PRIMARY KEY,
            link_name TEXT,
            link_url TEXT
        )
    """
    )
    conn.commit()
    conn.close()


async def middleware_channels():
    conn, cur = await connect_db()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS Middleware_Channels 
        (
            Channel_Name VARCHAR(255),
            Channel_Username VARCHAR(255) NOT NULL,
            Channel_Id VARCHAR(255) NOT NULL
        )        
    """
    )
    conn.commit()
    conn.close()
