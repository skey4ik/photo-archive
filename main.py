import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage

bot_token = ""

storage = MemoryStorage()
bot = Bot(bot_token)
dp = Dispatcher(bot, storage=storage)

class UserState(StatesGroup):
    photo = State()
    rar = State()
    name = State()

@dp.message_handler(commands=['start'])
async def start_command(message: types.message):
    await message.answer(f"Привет {message.from_user.first_name}\nЯ умею делать скрытый архив из картинки\n\n/archive - создать архив\n/cancel - отмена")

@dp.message_handler(commands=['archive'])
async def start_command(message: types.message):
    await message.answer("Отправь картинку")
    await UserState.photo.set()

@dp.message_handler(commands=['cancel'], state='*')
async def start_command(message: types.message, state: FSMContext):
    await message.answer("Операция отменена")
    await state.finish()


@dp.message_handler(content_types=['photo'], state=UserState.photo)
async def get_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = await bot.get_file(message.photo[-1].file_id)
    await message.answer("Отправь архив")
    await UserState.next()

@dp.message_handler(content_types=['document'], state=UserState.rar)
async def get_any(message: types.Message, state:FSMContext):
    async with state.proxy() as data:
        data['rar'] = await bot.get_file(message.document.file_id)
    await message.answer("Придумая название своему архиву и не используй символы")
    await UserState.next()

@dp.message_handler(state=UserState.name)
async def get_username(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    photo_extension = os.path.splitext(data['photo'].file_path)[1]
    photo_src = data['photo'].file_id + photo_extension
    await data['photo'].download(destination_file=photo_src)

    file_extention = os.path.splitext(data['rar'].file_path)[1]
    file_src = data['rar'].file_id + file_extention
    await data['rar'].download(destination_file=file_src)
    
    os.system(f"copy /b {photo_src} + {file_src} {data['name'] + photo_extension}")

    file = open(data['name'] + photo_extension, "rb")
    await bot.send_document(message.chat.id, file)
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)