import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from aiogram_dialog import Dialog, DialogManager, Window, DialogRegistry, BaseDialogManager, \
    StartMode
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Multi, Text

from typing import Any

from src.config import API_TOKEN


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


async def start_bg(c: CallbackQuery, button: Button, manager: DialogManager):
    await manager.start(Bg.progress)
    asyncio.create_task(background(c, manager.bg()))


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


main_menu = Dialog(
    Window(
        Const("Press button to start processing"),
        Button(Const("Start 👀"), id="start", on_click=start_bg),
        state=MainSG.main,
        getter=get_bg_data
    ),
)


async def start(m: Message, dialog_manager: DialogManager):
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
    dp.register_message_handler(start, text="/start", state="*")

    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())