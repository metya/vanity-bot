import re
import logging
import asyncio
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, executor, types
from aiogram_dialog import DialogManager, DialogRegistry, StartMode
from src.config import API_TOKEN
from src.dialog import dialog, MySG
from src.progress import bg_dialog
from src.summarize import get_paper_desc

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN) # type: ignore
dp = Dispatcher(bot, storage=MemoryStorage())
registry = DialogRegistry(dp)
registry.register(dialog)
registry.register(bg_dialog)

help_message = "Hello!\n\n\
Send me a link paper from arxiv.org and \
I'll send you back snippet of paper and arxiv-vanity.com mobile friendly link!\n\
Or add me to chat and I'll be watching the arxiv link and \
reply to them with fancy arxiv-vanity links."

async def deploy_message():
    await bot.send_message(chat_id=1147194, text='The deployment has been performed')

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply(help_message)


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply(help_message)
    
@dp.message_handler(commands=['long'])
async def long(message: types.Message):
    import random
    long = "".join(str(random.randint(1,10)) for _ in range(3700))
    await message.reply(long)


@dp.message_handler(regexp=r'arxiv.org\/(?:abs|pdf)\/\d{4}\.\d{5}')
async def vanitify(message: types.Message, dialog_manager: DialogManager):
    papers_ids = re.findall(r'arxiv.org\/(?:abs|pdf)\/(\d{4}\.\d{5}[v]?[\d]?)', message.text)
    
    async def start_dialog(manager=dialog_manager.bg(), state=MySG.main, mode=StartMode.NEW_STACK, data={}):
        await manager.start(state=state, mode=mode, data=data)

    async def get_paper_abs(id_):
        reply_message = f"[Here you maybe can read the paper in mobile friendly way](https://www.arxiv-vanity.com/papers/{id_})"
        data = {
            "id": id_,
            "reply_message": reply_message,
            "url": None,
            "title": None,
            "abs": None
        }
        if paper := await get_paper_desc(id_):
            id_, url, title, abstract, authors = paper.values()
            reply_message = f'{url}\n\n***{title}***\n\n{abstract}\n\n{reply_message}'
            data.update({
                "id": id_,
                "reply_message": reply_message,
                "url": url,
                "title": title,
                "abs": abstract,
                "authors": authors
                })
        else:
            reply_message = f'Something went wrong. Can not reach arxiv.com :('
            data["reply_message"] = reply_message
        return data

    list_data = await asyncio.gather(*[get_paper_abs(id_) for id_ in papers_ids])
    asyncio.gather(*[start_dialog(data=data) for data in list_data])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # logging.getLogger("asyncio").setLevel(logging.DEBUG)
    # logging.getLogger("aiogram_dialog").setLevel(logging.DEBUG)

    asyncio.get_event_loop().run_until_complete(deploy_message())
    executor.start_polling(dp, skip_updates=True)
