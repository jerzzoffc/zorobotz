import asyncio
import os

from pyrogram.errors import (ChannelPrivate, ChatSendPlainForbidden,
                             ChatWriteForbidden, FloodWait, Forbidden,
                             PeerIdInvalid, SlowmodeWait, UserBannedInChannel)

from config import DEVS, NO_GCAST, bot_username
from Userbot import nlx
from Userbot.helper.database import dB
from Userbot.helper.tools import Emojik, h_s, initial_ctext, zb

from .gcspam import extract_type_and_msg

__MODULES__ = "Broadcast"


def help_string(org):
    return h_s(org, "help_gcast")


@zb.ubot("bc")
async def _(c: nlx, m, _):
    em = Emojik(c)
    em.initialize()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = initial_ctext(c)
    msg = await m.reply(_("proses").format(em.proses, proses_))
    command, text = extract_type_and_msg(m)
    if command not in ["group", "private", "all"] or not text:
        await msg.edit(
            "{}**Silahkan gunakan format [`group`, `private` or `all`] [text/reply text]**".format(
                em.gagal
            )
        )
        return
    blacklist = dB.get_list_from_var(c.me.id, "BLGCAST")
    chats = await c.get_chats_dialog(command)
    done = 0
    failed = 0
    prefix = c.get_prefix(c.me.id)
    error = f"{em.gagal}**Error failed broadcast:**\n"
    for chat in chats:
        if chat in blacklist or chat in NO_GCAST or chat in DEVS:
            continue
        try:
            await (
                text.copy(chat) if m.reply_to_message else c.send_message(chat, text)
            )
            done += 1
        except ChannelPrivate:
            error += f"channel private {chat}\n"
            failed += 1

        except SlowmodeWait:
            error += f"gc di timer{chat}\n"
            failed += 1

        except ChatWriteForbidden:
            error += f"lu dimute {chat}\n"
            failed += 1

        except Forbidden:
            error += f"antispam grup aktif {chat}\n"
            failed += 1

        except ChatSendPlainForbidden:
            error += f"ga bisa kirim teks {chat}\n"
            failed += 1

        except UserBannedInChannel:
            error += f"lu limit {chat}\n"
            failed += 1

        except PeerIdInvalid:
            error += f"lu bukan pengguna grup ini {chat}\n"
            failed += 1

        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await (
                    text.copy(chat)
                    if m.reply_to_message
                    else c.send_message(chat, text)
                )
                done += 1
            except Exception as err:
                failed += 1
                error += f"{str(err)}\n"
        except Exception as err:
            failed += 1
            error += f"{str(err)} {chat}\n"
    await msg.delete()
    if error:
        error_dir = "errors"
        if not os.path.exists(error_dir):
            os.makedirs(error_dir)
        with open(f"{error_dir}/{c.me.id}_errors.txt", "w") as error_file:
            error_file.write(error)
        return await m.reply(
            f"""
<blockquote><b>{em.warn}{sukses_}</b>
  <b>{em.sukses}Success: {done}</b>
  <b>{em.gagal}Failed: {failed}</b>
  <b>{em.msg}Type: {command}</b>
  <b>{em.pong}Blacklist: {len(blacklist)} </b>
<b>Enter <code>{prefix[0]}bc-error</code> to view failed in broadcast.</b></blockquote>"""
        )
    else:
        return await m.reply(
            f"""
<blockquote><b>{em.warn}{sukses_}</b>
  <b>{em.sukses}Success: {done}</b>
  <b>{em.gagal}Failed: {failed}</b>
  <b>{em.msg}Type: {command}</b>
  <b>{em.pong}Blacklist: {len(blacklist)} </b> </blockquote>"""
        )


@zb.ubot("bc-error")
@zb.deve("bc-error")
async def _(client, message, _):
    oy = await message.reply("<b>Reading error logs...</b>")
    try:
        error_file = f"errors/{client.me.id}_errors.txt"
        try:
            with open(error_file, "r") as f:
                content = f.read().strip()

            if not content:
                await oy.edit("<b>No errors found in log file.</b>")
                return
            if len(content) > 4000:
                content = content[-4000:]
                content = f"... (truncated)\n\n{content}"

            message_text = f"<b>📋 Error Logs:</b>\n\n<code>{content}</code>"

            return await oy.edit(message_text)

        except FileNotFoundError:
            return await oy.edit("<b>Error log file not found!</b>")

    except Exception:
        try:
            error_file = f"errors/{client.me.id}_error.txt"
            with open(error_file, "r") as f:
                content = f.read().strip()

            if not content:
                await oy.edit("<b>No errors found in fallback log file.</b>")
                return

            if len(content) > 4000:
                content = content[-4000:]
                content = f"... (truncated)\n\n{content}"

            message_text = (
                f"<b>📋 Error Logs (from fallback):</b>\n\n<code>{content}</code>"
            )

            await client.send_message("me", message_text)
            return await oy.edit("<b>Cek saved message</b>")

        except Exception as e:
            return await oy.edit(f"<b>Failed to read error logs: {str(e)}</b>")


@zb.ubot("gcast")
@zb.deve("gcast")
async def _(c: nlx, m, _):
    em = Emojik(c)
    em.initialize()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = initial_ctext(c)
    msg = await m.reply(_("proses").format(em.proses, proses_))
    text = c.get_m(m)
    if not text:
        await msg.edit(_("gcs_1").format(em.gagal))
        return
    blacklist = dB.get_list_from_var(c.me.id, "BLGCAST")
    chats = await c.get_chats_dialog("group")
    done = 0
    failed = 0
    prefix = c.get_prefix(c.me.id)
    error = f"{em.gagal}**Error failed broadcast:**\n"
    for chat in chats:
        if chat in blacklist or chat in NO_GCAST:
            continue
        try:
            await (
                text.copy(chat) if m.reply_to_message else c.send_message(chat, text)
            )
            done += 1
        except ChannelPrivate:
            error += f"channel private {chat}\n"
            failed += 1

        except SlowmodeWait:
            error += f"gc di timer{chat}\n"
            failed += 1

        except ChatWriteForbidden:
            error += f"lu dimute {chat}\n"
            failed += 1

        except Forbidden:
            error += f"antispam grup aktif {chat}\n"
            failed += 1

        except ChatSendPlainForbidden:
            error += f"ga bisa kirim teks {chat}\n"
            failed += 1

        except UserBannedInChannel:
            error += f"lu limit\n"
            failed += 1

        except PeerIdInvalid:
            error += f"lu bukan pengguna grup ini {chat}\n"
            failed += 1

        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await (
                    text.copy(chat)
                    if m.reply_to_message
                    else c.send_message(chat, text)
                )
                done += 1
            except Exception as err:
                failed += 1
                error += f"{str(err)}\n"
        except Exception as err:
            failed += 1
            error += f"{str(err)}\n"
    await msg.delete()
    if error:
        error_dir = "errors"
        if not os.path.exists(error_dir):
            os.makedirs(error_dir)
        with open(f"{error_dir}/{c.me.id}_errors.txt", "w") as error_file:
            error_file.write(error)
        return await m.reply(
            f"""
<blockquote><b>{em.warn}{sukses_}</b>
  <b>{em.sukses}Success: {done}</b>
  <b>{em.gagal}Failed: {failed}</b>
  <b>{em.msg}Type: group</b>
  <b>{em.pong}Blacklist: {len(blacklist)} </b>
<b>Enter <code>{prefix[0]}bc-error</code> to view failed in broadcast.</b></blockquote>"""
        )
    else:
        return await m.reply(
            f"""
<blockquote><b>{em.warn}{sukses_}</b>
  <b>{em.sukses}Success: {done}</b>
  <b>{em.gagal}Failed: {failed}</b>
  <b>{em.pong}Blacklist: {len(blacklist)} </b>
  <b>{em.msg}Type: group</b></blockquote>"""
        )


@zb.ubot("ucast")
@zb.deve("ucast")
async def _(c: nlx, m, _):
    em = Emojik(c)
    em.initialize()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = initial_ctext(c)
    msg = await m.reply(_("proses").format(em.proses, proses_))
    text = c.get_m(m)
    if not text:
        await msg.edit(_("gcs_1").format(em.gagal))
        return
    blacklist = dB.get_list_from_var(c.me.id, "BLGCAST")
    chats = await c.get_chats_dialog("private")
    done = 0
    failed = 0
    for chat in chats:
        if chat in blacklist or chat in DEVS:
            continue
        try:
            await (
                text.copy(chat) if m.reply_to_message else c.send_message(chat, text)
            )
            done += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await (
                    text.copy(chat)
                    if m.reply_to_message
                    else c.send_message(chat, text)
                )
                done += 1
            except Exception:
                failed += 1
        except Exception:
            failed += 1
    await m.reply(_("gcs_16").format(em.owner, em.sukses, done, em.gagal, failed))
    await msg.delete()
    return


@zb.ubot("addbl")
@zb.deve("addbl")
@zb.devs("addbl")
async def _(c: nlx, m, _):
    em = Emojik(c)
    em.initialize()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = initial_ctext(c)
    pp = await m.reply(_("proses").format(em.proses, proses_))
    chat_id = m.command[1] if len(m.command) > 1 else m.chat.id
    blacklist = dB.get_list_from_var(c.me.id, "BLGCAST")
    try:
        chat_id = int(chat_id)
    except ValueError:
        return await pp.edit(
            "{}<b>KONTOL KONTOL KALO PAKE NONE PREFIX JANGAN ASAL KETIK GOBLOK\n\n BOT GW YANG EROR ANJ!!!</b>".format(
                em.gagal
            )
        )
    if chat_id in blacklist:
        return await pp.edit(_("gcs_4").format(em.sukses))
    chat = await c.get_chat(chat_id)
    dB.add_to_var(c.me.id, "BLGCAST", chat_id)
    return await pp.edit(_("gcs_5").format(em.sukses, chat.title))


@zb.ubot("delbl")
@zb.deve("delbl")
async def _(c: nlx, m, _):
    em = Emojik(c)
    em.initialize()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = initial_ctext(c)
    pp = await m.reply(_("proses").format(em.proses, proses_))

    blacklist = dB.get_list_from_var(c.me.id, "BLGCAST")
    try:
        chat_id = int(m.command[1]) if len(m.command) > 1 else m.chat.id
        if chat_id not in blacklist:
            return await pp.edit(_("gcs_7").format(em.gagal, chat_id))
        dB.remove_from_var(c.me.id, "BLGCAST", chat_id)
        chat = await c.get_chat(chat_id)
        return await pp.edit(_("gcs_8").format(em.gagal, chat.title))

    except Exception as error:
        return await pp.edit(str(error))


@zb.ubot("listbl")
async def _(c: nlx, m, _):
    em = Emojik(c)
    em.initialize()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = initial_ctext(c)
    pp = await m.reply(_("proses").format(em.proses, proses_))
    blacklist = dB.get_list_from_var(c.me.id, "BLGCAST")
    msg = _("gcs_10").format(em.sukses, len(blacklist))
    for x in blacklist:
        try:
            get = await c.get_chat(x)
            msg += _("gcs_11").format(get.title, get.id)
        except:
            msg += _("gcs_12").format(x)
    await pp.delete()
    return await m.reply(msg)


@zb.ubot("rmall")
async def _(c: nlx, m, _):
    em = Emojik(c)
    em.initialize()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = initial_ctext(c)
    msg = await m.reply(_("proses").format(em.proses, proses_))
    blacklist = dB.get_list_from_var(c.me.id, "BLGCAST")
    if blacklist is None:
        return await msg.edit(_("gcs_13").format(em.gagal))
    for x in blacklist:
        dB.remove_from_var(c.me.id, "BLGCAST", x)
    return await msg.edit(_("gcs_14").format(em.sukses))


@zb.ubot("send")
async def _(c: nlx, m, _):
    if m.reply_to_message:
        chat_id = m.chat.id if len(m.command) < 2 else m.text.split()[1]
        try:
            if m.reply_to_message.reply_markup:
                dB.set_var(c.me.id, "inline_send", id(m))
                x = await c.get_inline_bot_results(bot_username, f"_send_ {c.me.id}")
                await c.send_inline_bot_result(chat_id, x.query_id, x.results[0].id)
                await m.delete()
                return
        except Exception as error:
            return await m.reply(error)
        else:
            try:
                await m.reply_to_message.copy(chat_id)
                await m.delete()
                return
            except Exception as t:
                return await m.reply(f"{t}")
    else:
        if len(m.command) < 3:
            return
        chat_id, chat_text = m.text.split(None, 2)[1:]
        try:
            if "/" in chat_id:
                to_chat, msg_id = chat_id.split("/")
                await c.send_message(
                    to_chat, chat_text, reply_to_message_id=int(msg_id)
                )
                await m.delete()
                return
            else:
                await c.send_message(chat_id, chat_text)
                await m.delete()
                return
        except Exception as t:
            return await m.reply(f"{t}")
