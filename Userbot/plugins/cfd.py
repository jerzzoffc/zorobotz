import asyncio
import random
import os

from gc import get_objects
from asyncio import sleep
from pyrogram.raw.functions.messages import DeleteHistory, StartBot
from pyrogram.errors.exceptions import *
from pyrogram.errors.exceptions.not_acceptable_406 import ChannelPrivate

from pyrogram.errors import (ChannelPrivate, ChatSendPlainForbidden,
                             ChatWriteForbidden, FloodWait, Forbidden,
                             PeerIdInvalid, SlowmodeWait, UserBannedInChannel)

from config import DEVS, NO_GCAST, bot_username
from Userbot import nlx
from Userbot.helper.database import dB
from Userbot.helper.tools import Emojik, h_s, initial_ctext, zb

from .gcspam import extract_type_and_msg

__MODULES__ = "Cfd"


def help_string(org):
    return h_s(org, "help_cfd")


@zb.ubot("cfd")
async def _(client, message, *args):  
    _msg = f"proceꜱꜱing..."
    gcs = await message.reply(_msg)

    command, text = extract_type_and_msg(message)
    
    if command not in ["group", "private", "all"] or not text:
        return await gcs.edit(f"{message.text.split()[0]} type [reply]")

    if not message.reply_to_message:
        return await gcs.edit(f"{message.text.split()[0]} type [reply]")

    chats = await client.get_chats_dialog(command)
    blacklist = dB.get_list_from_var(client.me.id, "BLGCAST")

    done = 0
    failed = 0
    for chat_id in chats:
        if chat_id in blacklist or chat_id in NO_GCAST:
            continue

        try:
            if message.reply_to_message:
                await message.reply_to_message.forward(chat_id)
            else:
                await text.forward(chat_id)
            done += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            if message.reply_to_message:
                await message.reply_to_message.forward(chat_id)
            else:
                await text.forward(chat_id)
            done += 1
        except Exception:
            failed += 1
            pass

    await gcs.delete()
    _gcs = f"""
<blockquote><b>⌭ ʙʀᴏᴀᴅᴄᴀsᴛ ғᴏʀᴡᴀʀᴅ ᴅᴏɴᴇ</blockquote></b>
<blockquote><b>⌭ sᴜᴄᴄᴇs {done} ɢʀᴏᴜᴘ</b>
<b>⌭ ғᴀɪʟᴇᴅ {failed} ɢʀᴏᴜᴘ</blockquote></b>
"""
    return await message.reply(_gcs)
