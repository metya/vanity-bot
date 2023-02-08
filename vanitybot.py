import re
import logging
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, executor, types
from aiogram_dialog import DialogManager, DialogRegistry, StartMode
from config import API_TOKEN
from dialog import dialog, MySG
from summarize import get_paper_desc

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
registry = DialogRegistry(dp)
registry.register(dialog)

help_message = "Hello!\n\n\
Send me a link paper from arxiv.org and \
I'll send you back snippet of paper and arxiv-vanity.com mobile friendly link!\n\
Or add me to chat and I'll be watching the arxiv link and \
reply to them with fancy arxiv-vanity links."

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply(help_message)


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply(help_message)


@dp.message_handler(regexp=r'arxiv.org\/(?:abs|pdf)\/\d{4}\.\d{5}')
async def vanitify(message: types.Message, dialog_manager: DialogManager):
    papers_ids = re.findall(r'arxiv.org\/(?:abs|pdf)\/(\d{4}\.\d{5})', message.text)

    for id_ in papers_ids:
        reply_message = f"[Here you can read the paper in mobile friendly way](https://www.arxiv-vanity.com/papers/{id_})"
        data = {
            "id": id_,
            "reply_message": reply_message,
            "url": None,
            "title": None,
            "abs": None
        }
        if desc := get_paper_desc(id_):
            url, title, description = desc
            reply_message = f'{url}\n\n***{title}***\n\n{description}\n\n{reply_message}'
            data.update({
                "reply_message": reply_message,
                "url": url,
                "title": title,
                "abs": description
                })
        else:
            reply_message = f'Something went wrong. Can not reach arxiv.com :('
            data["reply_message"] = reply_message

        await dialog_manager.start(MySG.main, mode=StartMode.NEW_STACK, data=data)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    executor.start_polling(dp, skip_updates=True)