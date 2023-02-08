
from typing import Any
import operator
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Window, Dialog, DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Radio
from aiogram_dialog.widgets.text import Format
from aiogram.types import ParseMode

from summarize import get_paper_desc, get_key_moments, get_summary


class MySG(StatesGroup):
    main = State()

buttons = [
        ("Abstract", '1'),
        ("Summary", '2'),
        ("Key Moments", '3'),
    ]

async def get_data(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.current_context()
    item_id = data.widget_data.get('radio_buttons') #type: ignore
    p = {"text": "OOOPS!"}
    title = data.start_data["title"] #type: ignore
    url = data.start_data["url"] #type: ignore
    
    if data.dialog_data.get('abs'): #type: ignore
        abst = data.dialog_data.get('abs') #type: ignore
    else:
        data.dialog_data["abs"] = data.start_data["reply_message"] #type: ignore
        abst = data.dialog_data.get('abs') #type: ignore

    if item_id == "2":
        if data.dialog_data.get("summary"):
            summ = data.dialog_data["summary"]
            p = {"text": f"{url}\n\n***{title}***\n\n{summ}"}
    elif item_id == "3":
        if data.dialog_data.get("key_moments"):
            keys = data.dialog_data.get("key_moments")
            p = {"text": f"{url}\n\n***{title}***\n\n{keys}"}
    else:
        p = {"text": abst}
    return p


async def on_button_selected(c: CallbackQuery, widget: Any, manager: DialogManager, item_id: str):
    data = manager.current_context()
    if item_id == "2":
        if data.dialog_data.get('summary'):
            pass
        else:
            await c.answer("Getting Summary, please wait")
            summary = await get_summary(url = data.start_data["url"])
            data.dialog_data["summary"] = summary
    elif item_id == "3":
        if data.dialog_data.get("key_moments"):
            pass
        else:
            await c.answer("Getting Key Moments, please wait")
            key_moments = await get_key_moments(url=data.start_data["url"])
            data.dialog_data["key_moments"] = key_moments
    else:
        pass
        
    return {"text": item_id}



buttons_kbd = Radio(
    Format("✓ {item[0]}"),
    Format("{item[0]}"),
    id="radio_buttons",
    item_id_getter=operator.itemgetter(1),
    items=buttons,
    on_click=on_button_selected,
)

dialog = Dialog(
    Window(
        Format("{text}"),
        buttons_kbd,
        state=MySG.main,
        getter=get_data,
        parse_mode=ParseMode.MARKDOWN,
        # preview_data={"button": "1"}
    )
)


