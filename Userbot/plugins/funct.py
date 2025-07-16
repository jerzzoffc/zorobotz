import asyncio
import io
import os
import random
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
from pyrogram import filters
from pyrogram.errors import (FloodWait, InputUserDeactivated, PeerIdInvalid,
                             UserIsBlocked)
from pyrogram.helpers import ikb, kb
from pytz import timezone

from config import CMD_HELP, bot_username, owner_id
from Userbot import bot, nlx
from Userbot.assistant.buatub import setExpiredUser
from Userbot.helper.database import dB, db_path
from Userbot.helper.tools import Emojik, zb, unpacked4

@zb.bots("restore")
@zb.thecegers
async def _(c, m, _):
    user_id = m.from_user.id
    msg_text = await c.ask(
        user_id,
        "<blockquote><emoji id=5258336354642697821>⬇️</emoji> <i>Silahkan kirim document file .db!!</i>\n\n<emoji id=5258474669769497337>❗️</emoji> <i>Dan pastikan nama db_name sesuai dengan config.py</i></blockquote>",
        filters=filters.document,
    )
    document = msg_text.document
    if os.path.exists(db_path):
        os.remove(db_path)
    await c.download_media(document, "./")
    return await m.reply(
        f"<blockquote><emoji id=5260416304224936047>✅</emoji> <b><i>Sukses melakukan restore database!</i></b>\n\n<emoji id=5260687119092817530>🔄</emoji> <i>Silahkan ketik</i> <code>/reboot</code></blockquote>"
    )


@zb.callback("^close")
async def cb_close_hlp(c, cq, _):
    try:
        unPacked = unpacked4(cq.inline_message_id)
        return await c.delete_messages(unPacked.chat_id, unPacked.message_id)
    except:
        pass


@zb.callback("^close_mbot")
async def cb_close(c, cq, _):
    return await cq.message.delete()


@zb.bots("addprem")
@zb.seller
async def _(c: bot, m, _):
    return await add_prem_user(c, m, _)


@zb.ubot("addprem")
@zb.thecegers
async def _(c: nlx, m, _):
    kon = m.from_user.id
    seles = dB.get_list_from_var(bot.me.id, "seller", "user")
    if kon not in seles:
        return
    return await add_prem_user(c, m, _)


async def add_prem_user(c, message, _):
    user_id, get_bulan = await c.extract_user_and_reason(message)
    if not user_id:
        return await message.reply(f"<blockquote><emoji id=5260342697075416641>❌</emoji> <i>Format salah!</i>\n\n<emoji id=5258474669769497337>❗️</emoji> <code>{message.text}</code> [user_id/username - bulan]</blockquote>")
    try:
        get_id = (await c.get_users(user_id)).id
    except Exception as error:
        return await message.reply(str(error))
    if not get_bulan:
        get_bulan = 1
    premium = dB.get_list_from_var(bot.me.id, "PREM", "USERS")
    if get_id in premium:
        return await message.reply(
            f"<blockquote><emoji id=5258474669769497337>❗️</emoji> <i>Pengguna dengan ID</i>: <code>{get_id}</code> <i>sudah memiliki akses premium!</i></blockquote>"
        )
    triala = dB.get_list_from_var(bot.me.id, "user_trial", "user")

    dB.add_to_var(bot.me.id, "PREM", get_id, "USERS")
    if get_id in triala:
        dB.remove_from_var(bot.me.id, "user_trial", get_id, "user")
    if not dB.get_expired_date(get_id):
        await setExpiredUser(get_id)
    await message.reply(
        f"<blockquote><emoji id=5258185631355378853>⭐️</emoji> <b>Akses Premium berhasil diberikan kepada</b> <code>{get_id}</code>!\n\n<emoji id=5258093637450866522>🤖</emoji> <i>Silahkan ke</i> @{bot_username} <i>untuk membuat userbot\n• ketik /start bot\n• pilih [buat userbot]\n• ikuti petunjuknya</i></blockquote>"
    )
    try:
        await bot.send_message(
            get_id,
            f"<blockquote><emoji id=5260268501515377807>📣</emoji> <b>Selamat!</b>\n\n<emoji id=5258185631355378853>⭐️</emoji> <i>Akun anda telah mendapatkan akses premium untuk pembuatan userbot</i></blockquote>",
            reply_markup=kb(
                [[("✅ Lanjutkan Buat Userbot")]],
                resize_keyboard=True,
                one_time_keyboard=True,
            ),
        )
    except:
        pass
    return await bot.send_message(
        owner_id,
        f"<blockquote><emoji id=5260268501515377807>📣</emoji> <b>New Premium User</b>\n\n<emoji id=5256143829672672750>👤</emoji> <i>From</i>: <code>{message.from_user.id}</code>\n<emoji id=5258486128742244085>👥</emoji> <i>To</i>: <code>{get_id}</code></blockquote>",
        reply_markup=ikb(
            [
                [
                    ("👤 Account", f"profil {message.from_user.id}"),
                    ("Account 👤", f"profil {get_id}"),
                ]
            ]
        ),
    )


@zb.bots("unprem")
#@zb.seller
async def _(c: bot, m, _):
    return await un_prem_user(c, m, _)


@zb.ubot("unprem")
@zb.thecegers
async def _(c: nlx, m, _):
    kon = m.from_user.id
    seles = dB.get_list_from_var(bot.me.id, "seller", "user")
    if kon not in seles:
        return
    return await un_prem_user(c, m, _)


async def un_prem_user(c, message, _):
    user_id = await c.extract_user(message)
    if not user_id:
        return await message.reply("<blockquote><emoji id=5260342697075416641>❌</emoji> <i>Balas pesan pengguna atau berikan user_id/username</i></blockquote>")
    try:
        user = await c.get_users(user_id)
    except Exception as error:
        await message.reply(str(error))
    delpremium = dB.get_list_from_var(bot.me.id, "PREM", "USERS")

    if user.id not in delpremium:
        return await message.reply("<blockquote><emoji id=5258474669769497337>❗️</emoji> <i>User tidak ditemukan dalam database premium</i></blockquote>")
    dB.remove_from_var(bot.me.id, "PREM", user.id, "USERS")
    return await message.reply(f"<blockquote><emoji id=5260416304224936047>✅</emoji> <b>{user.mention}</b>\n<i>berhasil dihapus dari database premium</i></blockquote>")


@zb.bots("listprem")
@zb.thecegers
async def get_prem_user(c: bot, message, _):
    users = dB.get_list_from_var(bot.me.id, "PREM", "USERS")
    if not users:
        return await message.reply_text("<blockquote><emoji id=5258474669769497337>❗️</emoji> <i>Tidak ada user premium ditemukan~</i></blockquote>")
    text = f"<blockquote><emoji id=5258185631355378853>⭐️</emoji> <b>Daftar User Premium</b>\n"
    count = 0
    for user_id in users:
        try:
            user = await bot.get_users(user_id)
            expired = dB.get_expired_date(user_id)
            expired_str = (
                expired.astimezone(timezone("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M")
                if expired else "<i>Tidak terdata</i>"
            )
            count += 1
            text += f"\n{count}. <b>{user.first_name} {user.last_name or ''}</b> (<code>{user.id}</code>)\n⏳ <i>Expired:</i> <code>{expired_str}</code>"
        except Exception:
            # Jika gagal, tetap tampilkan ID-nya
            count += 1
            expired = dB.get_expired_date(user_id)
            expired_str = (
                expired.astimezone(timezone("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M")
                if expired else "<i>Tidak terdata</i>"
            )
            text += f"\n{count}. <b>Unknown</b> (<code>{user_id}</code>)\n<emoji id=5258258882022612173>⏲</emoji> <i>Expired:</i> <code>{expired_str}</code>"
    text += f"\n\n<emoji id=5258185631355378853>⭐️</emoji> <i>Total Premium User:</i> <b>{count}</b></blockquote>"
    await message.reply_text(text)

@zb.bots("addseller")
@zb.thecegers
async def _(c: bot, m, _):
    return await add_seller(c, m, _)


@zb.ubot("addseller")
@zb.thecegers
async def _(c: nlx, m, _):
    kon = m.from_user.id
    seles = dB.get_list_from_var(bot.me.id, "seller", "user")
    if kon not in seles:
        return
    return await add_seller(c, m, _)


async def add_seller(c, message, _):
    user = None
    user_id = await c.extract_user(message)
    if not user_id:
        return await message.reply(f"<emoji id=5258474669769497337>❗️</emoji> Balas pesan pengguna atau berikan user_id/username")
    try:
        user = await c.get_users(user_id)
    except Exception as error:
        await message.reply(str(error))
    seles = dB.get_list_from_var(bot.me.id, "seller", "user")
    if user.id in seles:
        return await message.reply("Sudah menjadi reseller.")

    dB.add_to_var(bot.me.id, "seller", user.id, "user")
    return await message.reply(f"<emoji id=5260416304224936047>✅</emoji> {user.mention} telah menjadi reseller")


@zb.bots("unseller")
@zb.thecegers
async def _(c: bot, m, _):
    return await un_seller(c, m, _)


@zb.ubot("unseller")
@zb.thecegers
async def _(c: nlx, m, _):
    kon = m.from_user.id
    seles = dB.get_list_from_var(bot.me.id, "seller", "user")
    if kon not in seles:
        return
    return await un_seller(c, m, _)


async def un_seller(c, message, _):
    user = None
    user_id = await c.extract_user(message)
    if not user_id:
        return await message.reply(f"<blockquote><emoji id=5258474669769497337>❗️</emoji> <i>Reply user atau berikan user_id/username!</i></blockquote>")
    try:
        user = await c.get_users(user_id)
    except Exception as error:
        await message.reply(f"<blockquote><emoji id=5258474669769497337>❗️</emoji> <i>{str(error)}</i></blockquote>")
    seles = dB.get_list_from_var(bot.me.id, "seller", "user")
    if user.id not in seles:
        return await message.reply(f"<blockquote><emoji id=5260342697075416641>❌</emoji> <i>User tidak ditemukan di database seller~</i></blockquote>")
    dB.remove_from_var(bot.me.id, "seller", user.id, "user")
    return await message.reply(f"<blockquote><emoji id=5260416304224936047>✅</emoji> <b>{user.mention}</b> <i>berhasil dihapus dari seller!</i></blockquote>")


@zb.bots("listseller")
@zb.thecegers
async def get_seles_user(c: bot, message, _):
    text = f"<blockquote><emoji id=5258204546391351475>💰</emoji> <b>List Seller</b>\n"
    count = 0
    seles = dB.get_list_from_var(bot.me.id, "seller", "user")
    for user_id in seles:
        try:
            user = await bot.get_users(user_id)
            count += 1
            userlist = f"• {count}: <b>{user.first_name} {user.last_name or ''}</b> [<code>{user.id}</code>]"
        except Exception:
            continue
        text += f"{userlist}\n"
    if count == 0:
        return await message.reply_text("<blockquote><emoji id=5260342697075416641>❌</emoji> <i>Tidak ada seller ditemukan~</i></blockquote>")
    else:
        text += f"\n<i>Total:</i> <b>{count}</b></blockquote>"
        return await message.reply_text(text)

# ... (existing imports and code)

@zb.bots("getprem")
@zb.thecegers
async def _(c: bot, message, _):
    users = dB.get_list_from_var(bot.me.id, "PREM", "USERS")
    if not users:
        return await message.reply(f"<blockquote><emoji id=5260342697075416641>❌</emoji> <i>Tidak ada pengguna premium ditemukan.</i></blockquote>")
    text = f"<blockquote><emoji id=5258185631355378853>⭐️</emoji> <b>Daftar User Premium</b>\n"
    count = 0
    for user_id in users:
        try:
            user = await bot.get_users(user_id)
            expired = dB.get_expired_date(user_id)
            expired_str = (
                expired.astimezone(timezone("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M")
                if expired else "<i>Tidak terdata</i>"
            )
            count += 1
            text += f"\n{count}. <b>{user.first_name} {user.last_name or ''}</b> (<code>{user.id}</code>)\n<emoji id=5258258882022612173>⏲</emoji> <i>Expired:</i> <code>{expired_str}</code>"
        except Exception:
            count += 1
            expired = dB.get_expired_date(user_id)
            expired_str = (
                expired.astimezone(timezone("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M")
                if expired else "<i>Tidak terdata</i>"
            )
            text += f"\n{count}. <b>Unknown</b> (<code>{user_id}</code>)\n⏳ <i>Expired:</i> <code>{expired_str}</code>"
    text += f"\n\n<emoji id=5258185631355378853>⭐️</emoji> <i>Total Premium User:</i> <b>{count}</b></blockquote>"
    await message.reply(text)

@zb.bots("getseller")
@zb.thecegers
async def _(c: bot, message, _):
    users = dB.get_list_from_var(bot.me.id, "seller", "user")
    if not users:
        return await message.reply("<blockquote><emoji id=5260342697075416641>❌</emoji> <i>Tidak ada seller ditemukan.</i></blockquote>")
    text = f"<blockquote><emoji id=5249231689695115145>📰</emoji> <b>Daftar Seller</b>\n"
    count = 0
    for user_id in users:
        try:
            user = await bot.get_users(user_id)
            expired = dB.get_expired_date(user_id)
            expired_str = (
                expired.astimezone(timezone("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M")
                if expired else "<i>Tidak terdata</i>"
            )
            count += 1
            text += f"\n{count}. <b>{user.first_name} {user.last_name or ''}</b> (<code>{user.id}</code>)\n<emoji id=5258258882022612173>⏲</emoji> <i>Expired:</i> <code>{expired_str}</code>"
        except Exception:
            continue
    text += f"\n\n<emoji id=5258204546391351475>💰</emoji> <i>Total Seller:</i> <b>{count}</b></blockquote>"
    await message.reply(text)
###

@zb.bots("time|setexpired")
#@zb.seller
async def _(c: bot, message, _):
    user_id, get_day = await c.extract_user_and_reason(message)
    if not user_id:
        return await message.reply(f"<blockquote><emoji id=5258474669769497337>❗️</emoji> <i>{message.text} user_id/username hari</i></blockquote>")
    try:
        get_id = (await c.get_users(user_id)).id
    except Exception as error:
        return await message.reply(f"<blockquote><emoji id=5260342697075416641>❌</emoji> <i>{str(error)}</i></blockquote>")
    if not get_day:
        get_day = 30
    now = datetime.now(timezone("Asia/Jakarta"))
    expire_date = now + timedelta(days=int(get_day))
    dB.set_expired_date(user_id, expire_date)
    return await message.reply(f"<blockquote><emoji id=5258258882022612173>⏲</emoji> <b>{get_id}</b> <i>aktif selama</i> <b>{get_day}</b> <i>hari!</i></blockquote>")


@zb.bots("cek|cekexpired")
@zb.seller
async def _(c: bot, message, _):
    user_id = await c.extract_user(message)
    if not user_id:
        return await message.reply(f"<blockquote><emoji id=5258474669769497337>❗️</emoji> <i>{message.text} user_id/username hari</i></blockquote>")
    expired_date = dB.get_expired_date(user_id)
    if not expired_date:
        return await message.reply(f"<blockquote><emoji id=5260342697075416641>❌</emoji> <i>{user_id} belum diaktifkan.</i></blockquote>")
    expir = expired_date.astimezone(timezone("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M")
    return await message.reply(f"<blockquote><emoji id=5258258882022612173>⏲</emoji> <b>{user_id}</b> <i>aktif sampai</i> <b>{expir}</b></blockquote>")


@zb.bots("unexpired")
@zb.seller
async def _(c: bot, message, _):
    user = None
    user_id = await c.extract_user(message)
    if not user_id:
        return await message.reply("<blockquote><emoji id=5258474669769497337>❗️</emoji> <i>User tidak ditemukan~</i></blockquote>")
    try:
        user = await c.get_users(user_id)
    except Exception as error:
        return await message.reply(f"<blockquote><emoji id=5260342697075416641>❌</emoji> <i>{str(error)}</i></blockquote>")
    dB.rem_expired_date(user.id)
    return await message.reply(f"<blockquote><emoji id=5260416304224936047>✅</emoji> <b>{user.id}</b> <i>expired dihapus!</i></blockquote>")


@zb.bots("bcbot|bcast|broadcast|bacot")
@zb.thecegers
async def bacotan(c, message, _):
    await message.delete()
    brod = dB.get_list_from_var(bot.me.id, "BROADCAST")
    y = None
    x = None
    if message.reply_to_message:
        x = message.reply_to_message.id
        y = message.chat.id
    if len(message.command) > 1:
        return await message.reply(
            "<blockquote><emoji id=5258474669769497337>❗️</emoji> <i>Sertakan/balas pesan yang ingin disiarkan!</i></blockquote>"
        )
    gl = 0
    kntl = 0
    jmbt = len(brod)
    for i in brod:
        try:
            m = (
                await bot.forward_messages(i, y, x)
                if message.reply_to_message
                else await bot.send_message(i, y, x)
            )
            kntl += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            m = (
                await bot.forward_messages(i, y, x)
                if message.reply_to_message
                else await bot.send_message(i, y, x)
            )
            kntl += 1
        except UserIsBlocked:
            dB.remove_from_var(bot.me.id, "BROADCAST", i)
            gl += 1
            continue
        except PeerIdInvalid:
            dB.remove_from_var(bot.me.id, "BROADCAST", i)
            gl += 1
            continue
        except InputUserDeactivated:
            dB.remove_from_var(bot.me.id, "BROADCAST", i)
            gl += 1
            continue
    return await message.reply(
        f"<blockquote><emoji id=5260268501515377807>📣</emoji> <b>Broadcast Selesai!</b>\n\n<emoji id=5260416304224936047>✅</emoji> <i>Berhasil ke</i> <b>{kntl}</b> user\n<emoji id=5260342697075416641>❌</emoji> <i>Gagal ke</i> <b>{gl}</b> user\n<emoji id=5256143829672672750>👤</emoji> <i>Total Target:</i> <b>{jmbt}</b></blockquote>",
    )


@zb.bots("trial")
@zb.thecegers
async def _(c: bot, message, _):
    user_id, get_day = await c.extract_user_and_reason(message)
    if not user_id:
        return await message.reply(f"<blockquote><emoji id=5258474669769497337>❗️</emoji> <i>{message.text} user_id/username hari</i></blockquote>")
    try:
        get_id = (await c.get_users(user_id)).id
    except Exception as error:
        return await message.reply(f"<blockquote><emoji id=5260342697075416641>❌</emoji> <i>{str(error)}</i></blockquote>")
    if not get_day:
        get_day = 30
    now = datetime.now(timezone("Asia/Jakarta"))
    expire_date = now + relativedelta(hours=int(get_day))
    dB.set_expired_date(user_id, expire_date)
    return await message.reply(f"<blockquote><emoji id=5258258882022612173>⏲</emoji> <b>{get_id}</b> <i>aktif selama</i> <b>{get_day}</b> <i>jam!</i></blockquote>")

@zb.bots("cektrial")
@zb.thecegers
async def _(c: bot, message, _):
    user_id = await c.extract_user(message)
    if not user_id:
        return await message.reply(f"<blockquote><emoji id=5258474669769497337>❗️</emoji> <i>Pengguna tidak ditemukan~</i></blockquote>")
    expired_date = dB.get_expired_date(user_id)
    if expired_date is None:
        return await message.reply(f"<blockquote><emoji id=5260342697075416641>❌</emoji> <i>{user_id} belum diaktifkan.</i></blockquote>")
    else:
        remaining_days = (expired_date - datetime.now()).days
        return await message.reply(
            f"<blockquote><emoji id=5258258882022612173>⏲</emoji> <b>{user_id}</b> <i>aktif hingga</i> <b>{expired_date.strftime('%d-%m-%Y %H:%M:%S')}</b>.<br><emoji id=5258419835922030550>🕔</emoji> <i>Sisa waktu aktif:</i> <b>{remaining_days}</b> hari</blockquote>"
        )


@zb.bots("untrial")
@zb.thecegers
async def _(c: bot, message, _):
    user = None
    user_id = await c.extract_user(message)
    if not user_id:
        return await message.reply("<blockquote>❌ <i>User tidak ditemukan~</i></blockquote>")
    try:
        user = await c.get_users(user_id)
    except Exception as error:
        return await message.reply(f"<blockquote>🚫 <i>{str(error)}</i></blockquote>")
    dB.rem_expired_date(user.id)
    return await message.reply(f"<blockquote>✅ <b>{user.id}</b> <i>expired dihapus!</i></blockquote>")


@zb.bots("top")
# @zb.thecegers
async def _(c: bot, m, _):
    return await get_top_module(c, m, _)


@zb.ubot("top")
# @zb.thecegers
async def _(c: nlx, m, _):
    em = Emojik(c)
    em.initialize()
    return await get_top_module(c, m, _)


"""
async def get_top_module(client, message, _):
    vars = dB.all_var(bot.me.id, "MODULES")
    # Convert string counts to integers
    sorted_vars = sorted(vars.items(), key=lambda item: int(item[1]), reverse=True)

    command_count = 999
    text = message.text.split()

    if len(text) == 2:
        try:
            command_count = min(max(int(text[1]), 1), 10)
        except ValueError:
            pass
    # Sum the integer values now
    total_count = sum(int(count) for _, count in sorted_vars[:command_count])

    txt = "<b>📊 Top Command</b>\n\n"
    for command, count in sorted_vars[:command_count]:
        txt += f"<b> •> {command} : {count}</b>\n"

    txt += f"\n<b>📈 Total: {total_count} Commands</b>"

    return await message.reply(txt)
"""


async def get_top_module(client, message, _):
    vars = dB.all_var(bot.me.id, "MODULES")
    sorted_vars = sorted(vars.items(), key=lambda item: int(item[1]), reverse=True)
    filtered_vars = [
        (command, count) for command, count in sorted_vars if int(count) > 50
    ]

    command_count = 999
    text = message.text.split()
    if len(text) == 2:
        try:
            command_count = min(max(int(text[1]), 1), 10)
        except ValueError:
            pass

    top_commands = filtered_vars[:command_count]
    total_count = sum(int(count) for i, count in sorted_vars[:command_count])

    txt = "<b>📊 Top Command</b>\n\n"
    txt += f"\n➡️ Diatas adalah data dari banyak nya command yang digunakan dari {len(CMD_HELP)} Module"
    txt += f"\n<b>📈 Total: {total_count} Commands</b>"

    if top_commands:
        graph = create_graph(top_commands)
        return await client.send_photo(
            chat_id=message.chat.id,
            photo=graph,
            caption=f"<b><blockquote>{txt}</blockquote></b>",
        )
    else:
        return await message.reply("<b>No commands with count greater than 50.</b>")


def create_graph(data):
    commands = [item[0].capitalize() for item in data]
    counts = [int(item[1]) for item in data]
    max_count = max(counts)
    colors = []

    for count in counts:
        if count == max_count:
            colors.append("blue")  # Warna biru untuk count tertinggi
        elif count > max_count * 0.5:
            colors.append("green")  # Warna hijau untuk count di atas 70% dari max
        elif count > max_count * 0.3:
            colors.append("yellow")  # Warna kuning untuk count di atas 40% dari max
        else:
            colors.append("red")  # Warna merah untuk count yang paling rendah

    plt.figure(figsize=(12, 8))
    bars = plt.bar(commands, counts, color=colors)
    plt.ylabel("Counts")
    plt.xlabel("Commands")
    plt.title("Top Command")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    # Mengatur label agar berada di atas batang
    for bar in bars:
        yval = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2, yval, int(yval), va="bottom", ha="center"
        )

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=300)
    buf.seek(0)
    plt.close()
    return buf


@zb.bots("addultra")
@zb.seller
async def _(c: bot, m, _):
    return await add_ultra_user(c, m, _)


@zb.ubot("addultra")
@zb.seller
async def _(c: nlx, m, _):
    return await add_ultra_user(c, m, _)


async def add_ultra_user(c, message, _):
    user_id, get_bulan = await c.extract_user_and_reason(message)
    if not user_id:
        return await message.reply(f"<b>{message.text} [user_id/username - bulan]</b>")
    try:
        get_id = (await c.get_users(user_id)).id
    except Exception as error:
        return await message.reply(str(error))
    if not get_bulan:
        get_bulan = 1
    ultraium = dB.get_list_from_var(bot.me.id, "PREM", "USERS")
    if get_id in ultraium:
        return await message.reply(
            f"Pengguna denga ID : `{get_id}` sudah memiliki akses !"
        )
    triala = dB.get_list_from_var(bot.me.id, "user_trial", "user")

    dB.add_to_var(bot.me.id, "PREM", get_id, "USERS")
    dB.add_to_var(bot.me.id, "USER_PREMIUM", get_id)
    if get_id in triala:
        dB.remove_from_var(bot.me.id, "user_trial", get_id, "user")
    if not dB.get_expired_date(get_id):
        await setExpiredUser(get_id)
    await message.reply(f"✅  <b>Akses diberikan kepada {get_id}!!")
    try:
        await bot.send_message(
            get_id,
            f"Selamat ! Akun anda sudah memiliki akses untuk pembuatan userbot",
            reply_markup=kb(
                [[("✅ Lanjutkan Buat Userbot")]],
                resize_keyboard=True,
                one_time_keyboard=True,
            ),
        )
    except:
        pass
    return await bot.send_message(
        owner_id,
        f"• {message.from_user.id} ─> {get_id} •",
        reply_markup=ikb(
            [
                [
                    ("👤 Account", f"profil {message.from_user.id}"),
                    ("Account 👤", f"profil {get_id}"),
                ]
            ]
        ),
    )


@zb.bots("unultra")
@zb.seller
async def _(c: bot, m, _):
    return await un_ultra_user(c, m, _)


@zb.ubot("unultra")
@zb.seller
async def _(c: nlx, m, _):
    return await un_ultra_user(c, m, _)


async def un_ultra_user(c, message, _):
    user_id = await c.extract_user(message)
    if not user_id:
        return await message.reply("Balas pesan pengguna atau berikan user_id/username")
    try:
        user = await c.get_users(user_id)
    except Exception as error:
        await message.reply(str(error))
    delultraium = dB.get_list_from_var(bot.me.id, "USER_PREMIUM")

    if user.id not in delultraium:
        return await message.reply("Tidak ditemukan")
    dB.remove_from_var(bot.me.id, "USER_PREMIUM", user.id)
    return await message.reply(f" ✅ {user.mention} berhasil dihapus")


@zb.bots("listultra")
@zb.thecegers
async def get_ultra_user(c: bot, message, _):
    text = ""
    count = 0
    for user_id in dB.get_list_from_var(bot.me.id, "USER_PREMIUM"):
        try:
            user = await bot.get_users(user_id)
            count += 1
            userlist = f"• {count}: <a href=tg://user?id={user.id}>{user.first_name} {user.last_name or ''}</a> > <code>{user.id}</code>"
        except Exception:
            continue
        text += f"{userlist}\n"
    if not text:
        return await message.reply_text("Tidak ada pengguna yang ditemukan")
    else:
        return await message.reply_text(text)

@zb.bots("joinseller")
async def _(c: bot, m, _):
    await m.reply(
        f"""
<blockquote><emoji id=5258474669769497337>❗️</emoji> <b>Rules For Reseller!</b>

<emoji id=5258331647358540449>✍️</emoji> <i>Persyaratan:</i>
• Memiliki basic dasar untuk berjualan
• Bertanggung jawab
• Tidak menjual Userbot ditempat lain (Only Moire-Userbot)
• Dilarang keras melakukan penipuan mengatasnamakan Moire-Userbot
• Memiliki Bank / E-wallet untuk transaksi

<emoji id=5258204546391351475>💰</emoji> <b>Keuntungan Reseller:</b>
• Mendapatkan harga seller yang lebih under
• Diberi akses seller Userbot (tidak perlu menunggu owner)
• Mendapat bimbingan di grup khusus seller
• Akses ke komunitas seller untuk berbagi peluang bisnis

<emoji id=5260416304224936047>✅</emoji><i>Jika Anda setuju dengan seluruh rules</i>
<emoji id=5316727448644103237>👤</emoji> <i>Hubungi</i>: @moire_mor <i>untuk pendaftaran</i></blockquote>""")
