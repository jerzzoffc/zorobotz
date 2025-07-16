import random
from pyrogram.enums import MessagesFilter
import requests

from Userbot.helper.tools import Emojik, h_s, zb
from Userbot import nlx

__MODULES__ = "Asupan"

def help_string(org):
    return h_s(org, "help_asupan")

@zb.ubot("asupan")
async def video_asupan(client, message, *args):
    y = await message.reply_text(f"💫 mencari video asupan...")
    try:
        asupannya = []
        async for asupan in client.search_messages(
            "@AsupanNyaSaiki", filter=MessagesFilter.VIDEO
        ):
            asupannya.append(asupan)
        video = random.choice(asupannya)
        await video.copy(message.chat.id, reply_to_message_id=message.id)
        await y.delete()
    except Exception as error:
        await y.edit(error)


@zb.ubot("cewek")
async def photo_cewek(client, message, *args):
    y = await message.reply_text(f"💫 mencari ayang...")
    try:
        ayangnya = []
        async for ayang in client.search_messages(
            "@AyangSaiki", filter=MessagesFilter.PHOTO
        ):
            ayangnya.append(ayang)
        photo = random.choice(ayangnya)
        await photo.copy(message.chat.id, reply_to_message_id=message.id)
        await y.delete()
    except Exception as error:
        await y.edit(error)
