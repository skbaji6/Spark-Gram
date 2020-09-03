import asyncio

from apscheduler.events import EVENT_JOB_SUBMITTED, EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telethon import events
import io

from telethon.tl import types
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, Message

from spark.util import admin_cmd

message_id = None
scheduler = None


def message_id_increment(event):
    if not event.exception:
        global message_id
        message_id = message_id + 1


@spark.on(admin_cmd(pattern="forward"))
async def _(event):
    global message_id
    message_id=int(event.text.split(" ")[1])-1
    scheduler = AsyncIOScheduler()
    scheduler.add_job(forward, 'interval', minutes=2, id='forward_job', args=[spark])

    # scheduler.add_job(test, 'interval', seconds=1, args=[message_id])
    # sscheduler.add_listener(message_id_increment, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    scheduler.start()


@spark.on(admin_cmd(pattern="stopforward"))
async def _(event):
    global scheduler
    scheduler.remove_job('forward_job')


async def forward(spark):
    try:
        groups = await spark.get_dialogs(offset_date=None, limit=1000)
        source_group = next((g for g in groups if g.id == -1001491824430), None)
        if source_group is not None:
            print("Found Source group")
            destination_user = await spark.get_entity(-1001297647039)
            global message_id
            async for message in spark.iter_messages(source_group, min_id=message_id, limit=1, reverse=True):
                message_id = message_id + 1
                if message.document is not None or message.video is not None:
                    print(message);
                    renameText = message.text
                    renameText = renameText.replace("HT BEATS", "").strip()
                    renameText = renameText.replace("- FIRST ON TELEGRAM", "").strip()
                    for ent, txt in message.get_entities_text():
                        if isinstance(ent, types.MessageEntityMention):
                            renameText = sanitize_text(renameText)
                            renameText = renameText.strip()
                            user = await spark.get_entity(577237895)
                    # await spark.sparkbot.send_message(user, "Processing file id: "+f"{message.id}")
                    sent_message: Message = await spark.send_message(destination_user, message)
                    await sent_message.reply("/tleech rename " + renameText)
                    await spark.send_message('me', f'Prorocessed id {message_id} with filename "{renameText}"')
    except Exception as e:
        spark._logger.exception("Something went wrong in forward")


async def test(param):
    global message_id
    message_id = message_id + 1
    print(message_id)

async def sanitize_text(input_text):
    sanitized_data = input_text.translate({ord(c): "-" for c in "+|"})
    sanitized_data = sanitized_data.translate({ord(c): "" for c in "™"})
    sanitized_data = sanitized_data.replace("  ","")
    return sanitized_data