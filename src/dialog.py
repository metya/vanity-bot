
import operator
from asyncio import sleep, create_task, gather, get_event_loop, Queue, current_task
from typing import Any, List
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Window, Dialog, DialogManager, StartMode, Data, BaseDialogManager
from aiogram_dialog.widgets.kbd import Radio
from aiogram_dialog.widgets.text import Format
from aiogram.types import ParseMode

from src.summarize import get_summary
from src.config import TIME_OUT
from src.progress import Bg, background

warn = "***Note, that it is an AI generated summary, and it may contain complete bullshit***"

class CrossData():
    queue: Queue = Queue()
    intent_queue: dict = {}
    context: dict = {}

class MySG(StatesGroup):
    main = State()

cross_data = CrossData()

buttons = [
        ("Abstract", '1'),
        ("Summary", '2'),
        ("Highlights", '3'),
        ("Findings", '4')
    ]


async def time_out_dialog(manager: BaseDialogManager, widget: Any, time_out: int|str|None = TIME_OUT):
    time_out = int(time_out) if time_out else 1800
    for _ in range(time_out):
        await sleep(1)
    await manager.update({"final_state": "1"})
    await sleep(1)
    await manager.done()


async def get_data(dialog_manager: DialogManager, **kwargs):
    text_message = {"text": "OOOPS!"}
    if data := dialog_manager.current_context():
        if cr_data:=cross_data.context.get(data.id):
            data.dialog_data.update(cr_data.dialog_data)
            del cross_data.context[data.id]
        else:
            cross_data.context[data.id] = None
        item_id = data.widget_data.get('radio_buttons') #type: ignore
        title = data.start_data["title"] #type: ignore
        url = data.start_data["url"] #type: ignore
        if ft:=data.dialog_data.get("final_state"):
            item_id = ft
        if data.dialog_data.get('abs'): #type: ignore
            abstract = data.dialog_data.get('abs') #type: ignore
        else:
            data.dialog_data["abs"] = data.start_data["reply_message"] #type: ignore
            abstract = data.dialog_data.get('abs') #type: ignore
        if item_id == "2":
            if summary:=data.dialog_data.get("summary"):
                if isinstance(summary, list):
                    while sum(len(sentence) for sentence in summary) > 3700:
                        summary = summary[:-1]
                    summary = " ".join(summary)
                text_message = {"text": f"{url}\n\n***{title}***\n\n{summary}\n\n{warn}"}
        elif item_id == "3":
            if highlights:=data.dialog_data.get("highlights"):
                if isinstance(highlights, list):
                    highlights = "\n\n- ".join(highlights)
                text_message = {"text": f"{url}\n\n***{title}***\n\n- {highlights}\n\n{warn}"}
        elif item_id == "4":
            if findings:=data.dialog_data.get("findings"):
                if isinstance(findings, list):
                    findings = "\n\n- ".join(findings)
                text_message = {"text": f"{url}\n\n***{title}***\n\n- {findings}\n\n{warn}"}
        else:
            text_message = {"text": abstract}
        return text_message
    else:
        return text_message


async def on_button_selected(c: CallbackQuery, widget: Any, manager: DialogManager, item_id: str):
    if context := manager.current_context():
        id_, url = context.start_data["id"], context.start_data["url"] # type: ignore
        context.widget_data["radio_buttons"] = item_id
        cross_data.intent_queue[context.id] = None
        cross_data.context[context.id] = context
        if item_id == "2":
            if context.dialog_data.get('summary'):
                pass 
            else:
                await c.answer("Getting summary, please wait")
                await manager.start(Bg.progress)
                gather(
                    background(c, manager.bg(), cross_data, context.id),
                    get_summary(cross_data=cross_data, paper_id=id_, paper_url=url, context_id=context.id),
                    )
        elif item_id == "3":
            if context.dialog_data.get("highlights"):
                pass
            else:
                await c.answer("Getting highlights, please wait")
                await manager.start(Bg.progress)
                gather(
                    background(c, manager.bg(), cross_data, context.id),
                    get_summary(cross_data=cross_data, paper_id=id_, paper_url=url, context_id=context.id)
                    )
        elif item_id == "4":
            if context.dialog_data.get("findings"):
                pass
            else:
                await c.answer("Getting findings, please wait")
                await manager.start(Bg.progress)
                gather(
                    background(c, manager.bg(), cross_data, context.id),
                    get_summary(cross_data=cross_data, paper_id=id_, paper_url=url, context_id=context.id)
                    )
        else:
            pass
    else:
        return {"text": 1}
        
    return {"text": item_id}


async def default_button(c: CallbackQuery, dialog_manager: DialogManager, **kwargs):
    if widget:=dialog_manager.dialog().find("radio_buttons"):
        await widget.set_checked(c, "1", dialog_manager)
    create_task(time_out_dialog(manager=dialog_manager.bg(), widget=widget))


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
        parse_mode=ParseMode.MARKDOWN, # type: ignore
        # preview_data={"button": "1"}
    ),
    on_start=default_button,
)