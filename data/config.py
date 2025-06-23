from environs import Env
from read_json import get_from_json

env = Env()
env.read_env()


BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = [int(x) for x in env.list("ADMINS")]
BOTUSERNAME = env.str("BOTUSERNAME")
admin_username = env.str("admin_username")
films_channel = env.str("films_channel")
films_channel_id = env.str("films_channel_id")
debug_group = env.str("debug_group")