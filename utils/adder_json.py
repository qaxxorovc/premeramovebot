import json

async def add_user_to_daily_count(user_id: int):
    file_path = "bot_information.json"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    user_list = data.get("daily_users_count", [])
    user_ids = [u["id"] for u in user_list]

    if user_id not in user_ids:
        user_list.append({"id": user_id})
        data["daily_users_count"] = user_list

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

def get_daily_users_count():
    try:
        with open("bot_information.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        users = data.get("daily_users_count", [])
        return len(users)
    except FileNotFoundError:
        return 0            