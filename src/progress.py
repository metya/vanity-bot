import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message, CallbackQuery, User
from aiogram.utils.exceptions import Throttled
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import CancelHandler, current_handler

from aiogram_dialog import Dialog, DialogManager, Window, DialogRegistry, BaseDialogManager, \
    StartMode
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Multi, Text, Format

from typing import Any, Callable, Dict, Awaitable, Union

try: 
    from src.config import API_TOKEN
except:
    from config import API_TOKEN

class TrickyUser(BaseMiddleware):
    def __init__(self, user_id: int,):
        super().__init__()
        self.default_user = user_id

    async def on_process_update(self, update, data):
        if message:=update.message:
            message.from_user.id = self.default_user
        if callback:=update.callback_query:
            callback.from_user.id = self.default_user
        # print(update)


class Processing(Text):
    def __init__(self, field: str, width: int = 10, filled="🟩", empty="⬜", when = None):
        super().__init__(when)
        self.field = field
        self.width = width
        self.filled = filled
        self.empty = empty

    async def _render_text(self, data: dict, manager: DialogManager) -> str:
        if manager.is_preview():
            percent = 15
        else:
            percent = data[self.field]
        rest = self.width - percent

        return f"processing: {self.filled * percent + self.empty * rest}"

# name progress dialog
class Bg(StatesGroup):
    progress = State()


async def get_bg_data(dialog_manager: DialogManager, **kwargs):
    if context := dialog_manager.current_context():
        return {"progress": context.dialog_data.get("progress", 0)}
    else:
        return {"progress": "OOOOPS"}


bg_dialog = Dialog(
    Window(
        Multi(
            Const("Summarizing is processing, please wait...\n"),
            Processing("progress", 10),
        ),
        state=Bg.progress,
        getter=get_bg_data,
    ),
)


# main dialog
class MainSG(StatesGroup):
    main = State()
    background = State()


async def start_bg(c: CallbackQuery, button: Button, dialog_manager: DialogManager, **kwargs):
    # await manager.start(Bg.progress)
    # asyncio.create_task(background(c, manager.bg()))
    await dialog_manager.dialog().switch_to(MainSG.background)
    await task_background(dialog_manager)


async def get_task_bg_data(dialog_manager: DialogManager, **kwargs):
    for key, val in kwargs.items():
        print(key, val)
    kwargs['aiogd_storage_proxy'].user_id = 1
    print(dialog_manager)
    return {"text": dialog_manager.current_context().dialog_data.get("text", "gay")} # type: ignore

async def task_background(manager: DialogManager):
    print(manager.current_context())
    for i in range(5):
        print(i)
        await manager.update({"text": f"pidor{i}"})
        await asyncio.sleep(1)

async def background(c: CallbackQuery,
                     manager: DialogManager | BaseDialogManager,
                     cross_data: Any = None,
                     context_id: str | None = None,
                     time_out = 40):
    i = 0
    time = 0
    await asyncio.sleep(1)
    while True and time < time_out:

        i = i + 1 if i < 10 else 0
        time += 1

        await manager.update({"progress": i})
        await asyncio.sleep(1)

        if mess:=cross_data.intent_queue[context_id]:
            if mess == 'done':
                del cross_data.intent_queue[context_id]
                await manager.done()
                return

    await manager.done()


async def back(c, button, dialog_manager):
    await dialog_manager.dialog().back()

main_menu = Dialog(
    Window(
        Const("Press button to start processing"),
        Button(Const("Start 👀"), id="start", on_click=start_bg),
        state=MainSG.main,
        getter=get_task_bg_data
    ),
    Window(
        Const("THIS IS BACKGROUND"),
        Format("{text}"),
        Button(Const("Back"), id='back', on_click=back),
        state=MainSG.background,
        getter=get_task_bg_data
    )
)


async def start(m: Message, dialog_manager: DialogManager, **kwargs):
    # print(kwargs)
    await dialog_manager.start(MainSG.main, mode=StartMode.RESET_STACK)


async def main():
    # real main
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("aiogram_dialog").setLevel(logging.DEBUG)
    storage = MemoryStorage()
    bot = Bot(token=API_TOKEN) # type: ignore
    dp = Dispatcher(bot, storage=storage)
    registry = DialogRegistry(dp)
    registry.register(bg_dialog)
    registry.register(main_menu)
    dp.middleware.setup(TrickyUser(1))
    dp.register_message_handler(start, text="/start", state="*")
    await dp.skip_updates()
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())