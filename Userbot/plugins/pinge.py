import os
import json
import asyncio
import psutil
import random
import requests
import re
import platform
import subprocess
import sys
import traceback
import aiohttp
import filetype
import wget
import math
from io import BytesIO, StringIO
import psutil
from pyrogram.enums import UserStatus
from pyrogram import *
from pyrogram import Client, filters
from pyrogram.types import Message
from asyncio import get_event_loop
from gc import get_objects
from pyrogram.raw import *
from pyrogram.raw.functions import Ping
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from asyncio import sleep
from pyrogram.raw.functions.messages import DeleteHistory, StartBot
from bs4 import BeautifulSoup
from io import BytesIO
from pyrogram.errors.exceptions import *
from pyrogram.errors.exceptions.not_acceptable_406 import ChannelPrivate
from pyrogram.enums import ChatAction, ParseMode
from pyrogram import filters
from httpx import AsyncClient, Timeout
################################################################
import random
################################################################
from datetime import datetime
from time import time

from pyrogram.raw.functions import Ping

from Userbot import nlx
from Userbot.helper.database import dB
from Userbot.helper.tools import (Emojik, get_time, h_s, initial_ctext, zb,
                                  start_time)


__MODULES__ = "Ping"


def help_string(org):
    return h_s(org, "help_pingst")

from pyrogram import filters
from config import bot_username

# ... (potongan import dan kode lain tetap)
# ... import dan kode lain tetap

@zb.ubot("pingx")
@zb.devs("mpingx")
@zb.deve("mpingx")
async def ping_(c, m, _):
    em = Emojik(c)
    em.initialize()
    start = datetime.now()
    await c.invoke(Ping(ping_id=0))
    end = datetime.now()
    upnya = await get_time((time() - start_time))
    duration = round((end - start).microseconds / 100000, 2)
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = initial_ctext(c)

    cmd_args = m.text.split()
    # Mode switcher
    if len(cmd_args) == 3 and cmd_args[1].lower() == "mode":
        mode = cmd_args[2].lower()
        if mode in ["text", "sticker", "button", "code"]:  # <-- "code" ditambah di sini
            dB.set_var(c.me.id, "PING_MODE", mode)
            await m.reply(f"Pingx mode set to {mode}!")
            return
        else:
            await m.reply("Pilihan mode hanya 'text', 'sticker', 'button', atau 'code'.")
            return

    mode = dB.get_var(c.me.id, "PING_MODE") or "text"
    sticker_id = dB.get_var(c.me.id, "PING_STICKER")
    _ping = f"""
<b>{em.ping}{pong_}:</b> <u>{duration}ms</u>
<b>{em.pong}{uptime_}:</b> <u>{upnya}</u>
<b>{em.owner}{owner_}</b>"""

    # Tambah handling mode code di sini
    if mode == "code":
        code_ping = f"""```[Ping result]
_Ping : {duration}ms
_Uptime : {upnya}
_{owner_}```"""
        await m.reply(code_ping)
        return

    if mode == "button":
        try:
            x = await c.get_inline_bot_results(bot_username, "pingx")
            await m.reply_inline_bot_result(x.query_id, x.results[0].id)
        except Exception as error:
            await m.reply(str(error))
        return

    if mode == "sticker" and sticker_id:
        await m.reply_sticker(sticker_id)
        await m.reply(_ping)
        return

    await m.edit(_ping)

@nlx.on_callback_query(filters.regex(r"^pingx_now_(\d+)$"))
async def pingx_now_callback(client, cq):
    em = Emojik(client)
    em.initialize()
    start = datetime.now()
    await client.invoke(Ping(ping_id=0))
    end = datetime.now()
    upnya = await get_time((time() - start_time))
    duration = round((end - start).microseconds / 100000, 2)
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = initial_ctext(client)
    _ping = f"""
<b>{em.ping}{pong_}:</b> <u>{duration}ms</u>
<b>{em.pong}{uptime_}:</b> <u>{upnya}</u>
<b>{em.owner}{owner_}</b>"""
    await cq.answer()
    try:
        await cq.message.reply(_ping, parse_mode="html", disable_web_page_preview=True)
    except Exception:
        await cq.message.edit(_ping, parse_mode="html", disable_web_page_preview=True)

@zb.ubot("setpingx")
async def setping_mode(c, m, _):
    if m.reply_to_message and m.reply_to_message.sticker:
        sticker_id = m.reply_to_message.sticker.file_id
        dB.set_var(c.me.id, "PING_STICKER", sticker_id)
        await m.reply("Sticker untuk pingx berhasil disimpan!")
    else:
        await m.reply("Reply ke sebuah sticker untuk menyimpan sebagai pingx sticker.")



@zb.ubot("ping")
@zb.devs("mping")
@zb.deve("mping")
async def ping_(c, m, _):
    em = Emojik(c)
    em.initialize()
    start = datetime.now()
    await c.invoke(Ping(ping_id=0))
    end = datetime.now()
    upnya = await get_time((time() - start_time))
    duration = round((end - start).microseconds / 100000, 2)
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = initial_ctext(c)
    _ping = f"""
<b>{em.ping}{pong_}:</b> <u>{duration}ms</u>
<b>{em.pong}{uptime_}:</b> <u>{upnya}</u>
<b>{em.owner}{owner_}</b>"""
    return await m.reply(_ping)


@zb.devs("teston")
@zb.deve("teston")
async def ping_(c, m, _):
    em = Emojik(c)
    em.initialize()
    start = datetime.now()
    await c.invoke(Ping(ping_id=0))
    end = datetime.now()
    duration = round((end - start).microseconds / 100000, 2)
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = initial_ctext(c)
    _ping = f"""
<b>{em.ping}{pong_}:</b> <u>{duration}ms</u>
<b>{em.owner}{owner_}</b>
<blockquote>ᴜsᴇʀʙᴏᴛ ᴏɴ ʙᴀɴɢ mor</blockquote>"""
    return await m.reply(_ping)



def add_absen(c, text):
    auto_text = dB.get_var(c.me.id, "TEXT_ABSEN") or []
    auto_text.append(text)
    dB.set_var(c.me.id, "TEXT_ABSEN", auto_text)


@zb.deve("absen")
@zb.devs("absen")
async def _(c: nlx, message, _):
    txt = dB.get_var(c.me.id, "TEXT_ABSEN")
    if len(message.command) == 1:
        if not txt:
            return
        try:
            psn = random.choice(txt)
            return await message.reply(psn)
        except:
            pass
    else:
        command, variable = message.command[:2]
        if variable.lower() == "text":
            for x in nlx._ubot:
                value = " ".join(message.command[2:])
                add_absen(x, value)

        else:
            return
