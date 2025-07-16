import asyncio
import datetime
from datetime import datetime as dt

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import bot_username
from Userbot import logger, nlx
from Userbot.helper.database import dB
from Userbot.helper.tools import Emojik, h_s, initial_ctext, zb, get_msg_button, create_inline_keyboard

__MODULES__ = "CekAkunTele"

def help_string(org):
    return h_s(org, "help_cekakuntele")
    
ID_ESTIMASI = [
    (1_000_000, datetime.datetime(2014, 10, 1)),
    (10_000_000, datetime.datetime(2015, 5, 1)),
    (100_000_000, datetime.datetime(2018, 4, 1)),
    (400_000_000, datetime.datetime(2020, 6, 1)),
    (900_000_000, datetime.datetime(2022, 5, 1)),
    (1_000_000_000, datetime.datetime(2022, 8, 1)),
    (2_000_000_000, datetime.datetime(2023, 6, 1)),
]

def unix_to_date(user_id: int):
    if user_id < 10_000_000:
        return datetime.datetime.utcfromtimestamp(user_id)
    return None

def estimasi_dari_id(user_id: int):
    if user_id < 10_000_000:
        return None
    for idx in range(len(ID_ESTIMASI) - 1, -1, -1):
        id_batas, tanggal_batas = ID_ESTIMASI[idx]
        if user_id >= id_batas:
            if idx + 1 < len(ID_ESTIMASI):
                id_batas2, tanggal_batas2 = ID_ESTIMASI[idx + 1]
                rasio = (user_id - id_batas) / (id_batas2 - id_batas)
                delta = tanggal_batas2 - tanggal_batas
                return tanggal_batas + rasio * delta
            return tanggal_batas
    return None

def format_umur(delta):
    tahun = delta.days // 365
    bulan = (delta.days % 365) // 30
    hari = (delta.days % 365) % 30
    return f"{tahun} tahun, {bulan} bulan, {hari} hari"

@zb.ubot("cekakun")
async def cek_umur_akun(client, message, _):
    user = message.reply_to_message.from_user if message.reply_to_message else None
    if not user:
        await message.reply_text("<blockquote><i><emoji id=5275969776668134187>⛔️</emoji> Reply pesan yang mau dicek umur akunnya.\nTidak dapat menemukan pengguna dari pesan yang tidak direply pesannya</i></blockquote>")
        return

    user_id = user.id
    text = f"<blockquote><b><emoji id=5316727448644103237>👤</emoji> Info Umur Akun Telegram</b>\n"
    text += f"<emoji id=5257965174979042426>📝</emoji> <b>Nama :</b> {user.first_name}"
    if user.last_name:
        text += f" {user.last_name}"
    text += f"\n<emoji id=5258503720928288433>ℹ️</emoji> <b>User ID :</b> <code>{user_id}</code></blockquote>\n"

    creation_date = unix_to_date(user_id)
    now = datetime.datetime.utcnow()
    if creation_date:
        delta = now - creation_date
        text += (
            f"<blockquote><emoji id=5258105663359294787>🗓</emoji> <b>Tanggal dibuat (presisi) :</b> <code>{creation_date.strftime('%d-%m-%Y')}</code>\n"
            f"<emoji id=5258362837411045098>👤</emoji> <b>Umur Akun :</b> {format_umur(delta)}\n"
            "<emoji id=5258331647358540449>✍️</emoji> <i>Presisi tinggi (akun Telegram lama)</i></blockquote>"
        )
    else:
        estimasi_date = estimasi_dari_id(user_id)
        if estimasi_date:
            delta = now - estimasi_date
            text += (
                f"<blockquote><emoji id=5258105663359294787>🗓</emoji> <b>Estimasi tanggal dibuat akun :</b> <code>{estimasi_date.strftime('%d-%m-%Y')}</code>\n"
                f"<emoji id=5258362837411045098>👤</emoji> <b>Estimasi umur akun :</b> {format_umur(delta)}\n</blockquote>"
                "<blockquote><emoji id=5258331647358540449>✍️</emoji> Estimasi berdasarkan statistik database range ID Telegram</blockquote>"
            )
        else:
            text += (
                "<blockquote><emoji id=5275969776668134187>⛔️</emoji> <b>Tidak dapat membaca tanggal pembuatan akun secara presisi.</b>\n"
                "<emoji id=5258474669769497337>❗️</emoji> <i>Telegram tidak membuka tanggal pembuatan akun untuk publik.</i></blockquote>"
            )

    await message.reply_text(text, disable_web_page_preview=True)


##
