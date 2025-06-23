# from aiogram.dispatcher.filters.state import State,StatesGroup

# class form(StatesGroup):
#     waiting_for_name = State()

# @dp.message_handler(commands='start')
# async def start_message(message: types.Message):
#     await message.reply("Salom! Ismingizni kiriting:")
#     await form.waiting_for_name.set()

# @dp.message_handler(state=form.waiting_for_name)
# async def process_name(message: types.Message, state: FSMContext):
#     await state.update_data(name=message.text) 