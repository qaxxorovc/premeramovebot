import json

FILE_PATH = "bot_information.json"


# ✅ 1. Ma'lumotni olish
def get_from_json(line_name: str):
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            value = data.get(line_name)
            if isinstance(value, str) and value.lower() in ["true", "false"]:
                return value.lower() == "true"
            return value
    except FileNotFoundError:
        return None


# ✅ 2. Ma'lumotni o‘zgartirish
def change_from_json(line_name: str, new_data):
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    data[line_name] = new_data

    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
