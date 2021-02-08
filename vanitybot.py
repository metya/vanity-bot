from aiogram.types import message
from aiogram.types.message import Message
from logzero import logger
import logging

from aiogram import Bot, Dispatcher, executor, types
from config import API_TOKEN

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Hello!\n\n\
Send me a link paper from arxiv.org and \
I'll send you back arxiv-vanity.com link with paper!\n\
Or add me to chat and I'll be watching the arxiv link and \
reply to them with fancy axiv-vanity links.")


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("Напиши мне что-нибудь, и я отпрпавлю этот текст тебе в ответ!")


# @dp.message_handler()
# async def echo_message(message: types.Message):
#     await bot.send_message(message.from_user.id, message.text)

@dp.message_handler(regexp='arxiv.org/\s*([^\s]*)')
async def cats(message: types.Message):
    id_paper = (message.text
                .replace('/abs', '')
                .replace('/pdf', '')
                .replace('.pdf', '')
                .split('/')[-1]
                .split(' ')[0])
    await message.reply(f'https://arxiv-vanity.com/papers/{id_paper}')
    # await bot.send_message(message.from_user.id, message.text)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)