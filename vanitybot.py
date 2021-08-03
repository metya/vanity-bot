import re
import logging
from attr import __description__
from logzero import logger
from aiogram.types import message
from aiogram.types.message import Message, ParseMode
from aiogram import Bot, Dispatcher, executor, types
from config import API_TOKEN
from bs4 import BeautifulSoup
from requests import get
from contextlib import suppress

# Configure logging
logging.basicConfig(level=logging.INFO)

# utils funtions
def get_paper_desc(id_paper: str) -> tuple:
    
    request = get(f'https://arxiv.org/abs/{id_paper}')
    if request.ok:
        soup = BeautifulSoup(request.content)
        with suppress(TypeError): 
            url = soup.find('meta', property='og:url').get('content')
            title = soup.find('meta', property='og:title').get('content')
            description = soup.find('meta', property='og:description').get('content').replace('\n', '')
            return url, title, description
    
    return None

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

help_message = "Hello!\n\n\
Send me a link paper from arxiv.org and \
I'll send you back snipet of paper and arxiv-vanity.com mobile friendly link!\n\
Or add me to chat and I'll be watching the arxiv link and \
reply to them with fancy axiv-vanity links."

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply(help_message)


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply(help_message)


@dp.message_handler(regexp='arxiv.org\/(?:abs|pdf)\/\d{4}\.\d{5}')
async def vanitify(message: types.Message):
    papers_ids = re.findall(r'arxiv.org\/(?:abs|pdf)\/(\d{4}\.\d{5})', message.text)
    
    for id_ in papers_ids:
        reply_message = f"[Here you can read the paper in mobile friendly way](https://www.arxiv-vanity.com/papers/{id_})"

        if desc := get_paper_desc(id_):
            url, title, description = desc
            reply_message = f'{url}\n\n***{title}***\n\n{description}\n\n{reply_message}'
        
            
        await message.reply(reply_message, parse_mode=ParseMode.MARKDOWN)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)