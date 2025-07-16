
import asyncio
import random
import os

from datetime import datetime

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
#creator : @moire_mor
__MODULES__ = "Jasebint"

def help_string(org):
    return h_s(org, "help_jasebint")

# Variabel global untuk status modul dan pengaturan delay/interval/limit
MODULE_STATUS = {
    "enabled": True,
    "delay_per_group": 0.5,
    "interval_delay": 10,
    "limit_interval": None,    # Limit jumlah interval broadcast
    "interval_count": 0,
}

def get_current_time_str():
    return datetime.now().strftime("%d/%m/%Y %H:%M")

def reset_interval_count(client):
    MODULE_STATUS["interval_count"] = 0
    dB.set_var(client.me.id, "JASEBINT_INTERVAL_COUNT", 0)

def load_interval_count(client):
    MODULE_STATUS["interval_count"] = dB.get_var(client.me.id, "JASEBINT_INTERVAL_COUNT") or 0

def save_interval_count(client):
    dB.set_var(client.me.id, "JASEBINT_INTERVAL_COUNT", MODULE_STATUS["interval_count"])

def load_limit_interval(client):
    MODULE_STATUS["limit_interval"] = dB.get_var(client.me.id, "JASEBINT_LIMIT_INTERVAL") or None

def save_limit_interval(client):
    dB.set_var(client.me.id, "JASEBINT_LIMIT_INTERVAL", MODULE_STATUS["limit_interval"])

@zb.ubot("jasebint")
async def jasebint_handler(client, message, _):
    """
    Fungsi utama untuk mengatur modul Jasebint dan melakukan broadcast.
    Gunakan perintah:
    - `jasebint on`: Mengaktifkan modul
    - `jasebint off`: Menonaktifkan modul
    - `jasebint delay <angka>`: Mengatur delay antar pengiriman ke grup (dalam detik)
    - `jasebint interval <angka>`: Mengatur interval antara sesi broadcast berikutnya (dalam menit)
    - `jasebint status`: Menampilkan status modul
    - `jasebint broadcast`: Melakukan broadcast (balas ke pesan yang ingin di-broadcast)
    - `jasebint limit interval <angka>`: Mengatur batas maksimal interval broadcast sebelum auto-off
    """
    # Inisialisasi nilai dari database saat fungsi dipanggil
    MODULE_STATUS["enabled"] = dB.get_var(client.me.id, "JASEBINT_ENABLED") or True
    MODULE_STATUS["delay_per_group"] = dB.get_var(client.me.id, "JASEBINT_DELAY") or 0.5
    MODULE_STATUS["interval_delay"] = dB.get_var(client.me.id, "JASEBINT_INTERVAL") or 10
    load_limit_interval(client)
    load_interval_count(client)

#@moire_mor    # === Pengecekan limit interval, jika sudah tercapai, auto off ===
    if MODULE_STATUS["limit_interval"] is not None and MODULE_STATUS["enabled"]:
        try:
            limit_interval = int(MODULE_STATUS["limit_interval"])
            if MODULE_STATUS["interval_count"] >= limit_interval:
                MODULE_STATUS["enabled"] = False
                dB.set_var(client.me.id, "JASEBINT_ENABLED", False)
                MODULE_STATUS["limit_interval"] = None
                save_limit_interval(client)
                reset_interval_count(client)
                await message.reply(
                    "<blockquote><i><emoji id=5350423812133381005>🕔</emoji> Limit interval tercapai!</i>\n"
                    "<i>Modul Jasebint dinonaktifkan otomatis setelah mencapai interval broadcast yang ditentukan.</i></blockquote>"
                )
        except Exception:
            MODULE_STATUS["limit_interval"] = None
            save_limit_interval(client)

    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) < 2:
        return await message.reply("<blockquote><b><emoji id=5319112319429523945>⛔️</emoji> Perintah tidak lengkap!</b></blockquote>\n<blockquote><b><emoji id=5316554554735607106>⚠️</emoji> Gunakan .jasebint help untuk bantuan</b></blockquote>")

    command = command_parts[1].lower().split(maxsplit=2)
    action = command[0]

    # Fitur on/off
    if action == "on":
        MODULE_STATUS["enabled"] = True
        dB.set_var(client.me.id, "JASEBINT_ENABLED", True)
        reset_interval_count(client)
        await message.reply("<blockquote><b><emoji id=4916036072560919511>✅</emoji> Modul Jasebint telah diaktifkan!</b>\n └<i> Status: Online dan siap digunakan</i></blockquote>")
    elif action == "off":
        MODULE_STATUS["enabled"] = False
        dB.set_var(client.me.id, "JASEBINT_ENABLED", False)
        reset_interval_count(client)
        await message.reply("<blockquote><b><emoji id=4918014360267260850>⛔️</emoji> Modul Jasebint telah dinonaktifkan!</b>\n └<i> Status: Offline</i></blockquote>")
#@moire_mor
    # Pengaturan delay antar grup
    elif action == "delay":
        if len(command) < 2 or not command[1].replace('.', '', 1).isdigit():
            return await message.reply("<blockquote><b><emoji id=4918014360267260850>⛔️</emoji> Format tidak valid!</b>\n└<i> Silakan masukkan angka untuk delay (dalam detik)</i></blockquote>")
        delay_value = float(command[1])
        MODULE_STATUS["delay_per_group"] = delay_value
        dB.set_var(client.me.id, "JASEBINT_DELAY", delay_value)
        await message.reply(f"<blockquote><b><emoji id=4916036072560919511>✅</emoji> Pengaturan Delay Berhasil!</b>\n └<i> Delay per grup: {delay_value} detik</i></blockquote>")
#@moire_mor
    elif action == "time":
        timenow = get_current_time_str()
        await message.reply(
            f"<blockquote><b><emoji id=5350595795508814391>🕓</emoji> Waktu Server Saat Ini</b>\n └<i> <code>{timenow}</code></i></blockquote>"
        )

    # Pengaturan interval antar sesi broadcast
    elif action == "interval":
        if len(command) < 2 or not command[1].replace('.', '', 1).isdigit():
            return await message.reply("<blockquote><b><emoji id=4918014360267260850>⛔️</emoji> Format tidak valid!</b>\n └<i> Silakan masukkan angka untuk interval (dalam menit)</i></blockquote>")
        interval_value = float(command[1])
        MODULE_STATUS["interval_delay"] = interval_value
        dB.set_var(client.me.id, "JASEBINT_INTERVAL", interval_value)
        await message.reply(f"<blockquote><b><emoji id=4916036072560919511>✅</emoji> Pengaturan Interval Berhasil!</b>\n └<i> Interval broadcast: {interval_value} menit</i></blockquote>")

    # Menampilkan status modul (tambah timenow & interval count & limit interval)
    elif action == "status":
        MODULE_STATUS["enabled"] = dB.get_var(client.me.id, "JASEBINT_ENABLED") or False
        load_interval_count(client)
        load_limit_interval(client)
        status = "Aktif" if MODULE_STATUS["enabled"] else "Nonaktif"
        delay_per_group = MODULE_STATUS["delay_per_group"]
        interval_delay = MODULE_STATUS["interval_delay"]
        limit_interval = MODULE_STATUS["limit_interval"] or "Tidak diatur"
        timenow = get_current_time_str()
        interval_count = MODULE_STATUS["interval_count"]
        await message.reply(f"""<blockquote><b><emoji id=5350404703823883106>⭐️</emoji> Status Modul Jasebint Day <emoji id=5350404703823883106>⭐️</emoji></b></blockquote>
<blockquote>╭─❖ Info Pengaturan
├ <emoji id=5350806480834553770>🛡</emoji> Status                    :  {'🟢 Online' if status == 'Aktif' else '🔴 Offline'}
├ <emoji id=5350423812133381005>🕔</emoji> Delay                      :  {delay_per_group}s/grup
├ <emoji id=5350289074714338146>⏳</emoji> Interval Delay       :  {interval_delay}m
├ <emoji id=5353079798434394021>✈️</emoji> Interval ke             :  {interval_count}
├ <emoji id=5350381992036820471>🛡</emoji> Limit Interval           :  {limit_interval}
├ <emoji id=5352940967911517739>⏳</emoji> TimeNow Server :  {timenow}</blockquote>
        """)
#@moire_mor
    # Fitur limit interval
    elif action == "limit":
        if len(command) < 3 or command[1] != "interval" or not command[2].isdigit():
            return await message.reply(
                "<blockquote><b><emoji id=4918014360267260850>⛔️</emoji> Format tidak valid!</b>\n"
                "└<i> Gunakan: jasebint limit interval <jumlah></i></blockquote>"
            )
        try:
            limit = int(command[2])
            MODULE_STATUS["limit_interval"] = limit
            save_limit_interval(client)
            await message.reply(
                f"<blockquote><b><emoji id=5352848733488834757>✔️</emoji> Limit Interval Berhasil Diatur!</b>\n"
                f" └<i> Setelah {limit} kali interval broadcast, modul akan otomatis off</i></blockquote>"
            )
        except ValueError:
            return await message.reply(
                "<blockquote><b><emoji id=4918014360267260850>⛔️</emoji> Format angka salah!</b>\n"
                "└<i> Gunakan angka misal: jasebint limit interval 6</i></blockquote>"
            )

    # Fitur broadcast dengan auto-off jika limit interval tercapai
    elif action == "broadcast":
        if not MODULE_STATUS["enabled"]:
            return await message.reply("<blockquote><b><emoji id=4918014360267260850>⛔️</emoji> Modul nonaktif!</b>\n └<i> Aktifkan dengan perintah : jasebint on</i></blockquote>")
        _msg = "<blockquote><i><emoji id=5316571734604790521>🚀</emoji> Proses broadcast sedang berjalan...</i></blockquote>"
        gcs = await message.reply(_msg)
        if not message.reply_to_message:
            return await gcs.edit("<blockquote><b><emoji id=4918014360267260850>⛔️</emoji> Pesan tidak ditemukan!</b>\n └<i> Balas ke pesan yang ingin di-broadcast</i></blockquote>")
        limit_interval = MODULE_STATUS["limit_interval"]
        auto_off_notified = False
        load_interval_count(client)
        while MODULE_STATUS["enabled"]:
            MODULE_STATUS["enabled"] = dB.get_var(client.me.id, "JASEBINT_ENABLED") or True
            MODULE_STATUS["delay_per_group"] = dB.get_var(client.me.id, "JASEBINT_DELAY") or 0.5
            MODULE_STATUS["interval_delay"] = dB.get_var(client.me.id, "JASEBINT_INTERVAL") or 10
            load_limit_interval(client)
            limit_interval = MODULE_STATUS["limit_interval"]
            # Cek limit interval
            if limit_interval is not None:
                try:
                    limit_interval = int(limit_interval)
                    if MODULE_STATUS["interval_count"] >= limit_interval:
                        MODULE_STATUS["enabled"] = False
                        dB.set_var(client.me.id, "JASEBINT_ENABLED", False)
                        MODULE_STATUS["limit_interval"] = None
                        save_limit_interval(client)
                        reset_interval_count(client)
                        if not auto_off_notified:
                            await message.reply(
                                "<blockquote><b><emoji id=5350289074714338146>⏳</emoji> Limit interval tercapai!</b>\n<i>Modul dinonaktifkan otomatis setelah jumlah interval broadcast yang ditentukan.</i></blockquote>"
                            )
                            auto_off_notified = True
                        break
                except Exception:
                    break
            if not MODULE_STATUS["enabled"]:
                reset_interval_count(client)
                break
            chats = await client.get_chats_dialog("group")
            blacklist = dB.get_list_from_var(client.me.id, "BLGCAST")
            done, failed = 0, 0
            for chat_id in chats:
                if chat_id in blacklist:
                    continue
                try:
                    await message.reply_to_message.forward(chat_id)
                    done += 1
                    await asyncio.sleep(MODULE_STATUS["delay_per_group"])
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                except Exception:
                    failed += 1
                    continue
            await gcs.delete()
            delay_per_group = MODULE_STATUS["delay_per_group"]
            interval_delay = MODULE_STATUS["interval_delay"]
            limit_interval_disp = MODULE_STATUS["limit_interval"] or "Tidak diatur"
            timenow = get_current_time_str()
            MODULE_STATUS["interval_count"] += 1
            save_interval_count(client)
            interval_count = MODULE_STATUS["interval_count"]
            _gcs = f"""
<blockquote><b><emoji id=5350404703823883106>⭐️</emoji> Hasil Broadcast <emoji id=5350404703823883106>⭐️</emoji></b></blockquote>
<blockquote>╭─❖ Ringkasan
├ <emoji id=4916036072560919511>✅</emoji> Status         : Selesai
├ <emoji id=5352848733488834757>✔️</emoji> Berhasil       : {done} grup
├ <emoji id=4918014360267260850>⛔️</emoji> Gagal          : {failed} grup
├ <emoji id=5350423812133381005>🕔</emoji> Delay          : {delay_per_group}s/grup
├ <emoji id=5350289074714338146>⏳</emoji> Interval delay : {interval_delay}m
├ <emoji id=5353079798434394021>✈️</emoji> Interval ke    : {interval_count}
├ <emoji id=5350381992036820471>🛡</emoji> Limit Interval : {limit_interval_disp}
├ <emoji id=5352940967911517739>⏳</emoji> TimeNow Server : {timenow}</blockquote>
            """
            await message.reply(_gcs)
            if MODULE_STATUS["enabled"]:
                await asyncio.sleep(MODULE_STATUS["interval_delay"] * 60)
        reset_interval_count(client)

    # Bantuan dan perintah tidak valid
    else:
        await message.reply(
            "<blockquote><b><emoji id=4918014360267260850>⛔️</emoji> Perintah tidak valid!</b></blockquote>\n"
            "<blockquote><b>• <emoji id=5350666288807046023>⚙️</emoji> Gunakan perintah berikut:</b>\n"
            "<i>• <emoji id=5350603376126094305>💡</emoji> jasebint on - Aktifkan modul</i>\n"
            "<i>• <emoji id=4918014360267260850>⛔️</emoji> jasebint off - Nonaktifkan modul</i>\n"
            "<i>• <emoji id=5350423812133381005>🕔</emoji> jasebint delay <angka> - Atur delay</i>\n"
            "<i>• <emoji id=5350289074714338146>⏳</emoji> jasebint interval <angka> - Atur interval</i>\n"
            "<i>• <emoji id=5350381992036820471>🛡</emoji> jasebint limit interval <angka> - Batasi total interval sebelum auto-off</i>\n"
            "<i>• <emoji id=5350666288807046023>⚙️</emoji> jasebint status - Menampilkan status pengaturan modul</i>\n"
            "<i>• <emoji id=5350595795508814391>🕓</emoji> jasebint time - Menampilkan waktu Server saat ini</i>\n"
            "<i>• <emoji id=5316571734604790521>🚀</emoji> jasebint broadcast - Broadcast pesan</i></blockquote>"
        )
