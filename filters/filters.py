from data.config import ADMINS
from aiogram.dispatcher.filters import Filter
from aiogram import types

class IsAdmin(Filter):
    async def check(self, message: types.Message) -> bool:
        if message.from_user.id in ADMINS:
            return True
        else:
            return False
        
async def IsAdminFunksion(id):
    if id in ADMINS:
        return True
    else:
        return False
