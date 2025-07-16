import asyncio

from pyrogram import enums
from pyrogram.enums import *
from pyrogram.errors import (ChannelPrivate, ChatAdminRequired, FloodWait,
                             UserNotParticipant)

from config import NO_GCAST
from Userbot import nlx
from Userbot.helper.database import dB
from Userbot.helper.tools import Emojik, h_s, initial_ctext, zb

__MODULES__ = "JoinLeave"
USER_PREMIUM = True


def help_string(org):
    return h_s(org, "help_join")


@zb.ubot("getmute")
@zb.deve("getmute")
async def _(client, message, _):
    em = Emojik(client)
    em.initialize()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = initial_ctext(client)
    output = ""
    msg = await message.reply(f"{em.proses}**{proses_}**")

    async for dialog in client.get_dialogs():
        if dialog.chat.type in (enums.ChatType.GROUP, enums.ChatType.SUPERGROUP):
            try:
                member = await client.get_chat_member(dialog.chat.id, client.me.id)
                if member.status == enums.ChatMemberStatus.RESTRICTED:
                    chat = await client.get_chat(dialog.chat.id)
                    output += f"{chat.title} | [`{chat.id}`]\n"
            except Exception:
                continue

    if output:
        text = f"<blockquote><b>Daftar group yang membisukan anda adalah:</b>\n{output}</blockquote>"
    else:
        text = "<blockquote>Daftar group yang membisukan anda kosong</blockquote>"

    return await msg.edit(text)


@zb.ubot("join")
@zb.devs("Cjoin")
async def _(c, m, _):
    em = Emojik(c)
    em.initialize()
    Nan = m.command[1] if len(m.command) > 1 else m.chat.id
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = initial_ctext(c)
    ceger = await m.reply_text(_("proses").format(em.proses, proses_))
    try:
        chat_id = m.command[1] if len(m.command) > 1 else m.chat.id
        if chat_id.startswith("https://t.me/"):
            chat_id = chat_id.split("/")[-1]
        inpogc = await c.get_chat(Nan)
        namagece = inpogc.title

        await ceger.edit(_("join_1").format(em.sukses, namagece))
        await c.join_chat(Nan)
        return
    except Exception as ex:
        await ceger.edit(_("err").format(em.gagal, ex))
        return


@zb.ubot("kickme")
@zb.devs("Ckickme")
async def _(c, m, _):
    em = Emojik(c)
    em.initialize()
    namagece = m.chat.title
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = initial_ctext(c)
    ceger = await m.reply(_("proses").format(em.proses, proses_))
    try:
        chat_member = await c.get_chat_member(m.chat.id, m.from_user.id)
        if chat_member.status in (
            enums.ChatMemberStatus.ADMINISTRATOR,
            enums.ChatMemberStatus.OWNER,
        ):
            await ceger.edit(_("join_7").format(em.gagal, namagece))
            return

        if len(m.command) < 2:
            chat_id = m.chat.id
            namagece = m.chat.title
            if chat_id in NO_GCAST:
                await ceger.edit(_("join_2").format(em.gagal, namagece))
                return
            else:
                await ceger.edit(_("join_3").format(em.sukses, c.me.mention, namagece))
                await c.leave_chat(chat_id)
                return

        chat_arg = m.command[1]

        if chat_arg.startswith("@"):
            inpogc = await c.get_chat(chat_arg)
            chat_id = inpogc.id
            namagece = inpogc.title

            if chat_id in NO_GCAST:
                return await ceger.edit(_("join_2").format(em.gagal, namagece))
            else:
                await ceger.edit(_("join_3").format(em.sukses, c.me.mention, namagece))
                return await c.leave_chat(chat_id)

        elif chat_arg.startswith("https://t.me/"):
            chat_id = chat_arg.split("/")[-1]
            inpogc = await c.get_chat(chat_id)
            namagece = inpogc.title
            if str(chat_id) in NO_GCAST or inpogc.id in NO_GCAST:
                await ceger.edit(_("join_2").format(em.gagal, namagece))
                return
            else:
                await ceger.edit(_("join_3").format(em.sukses, c.me.mention, namagece))
                await c.leave_chat(chat_id)
                return

        else:
            await m.reply(_("join_4").format(em.sukses))
            await c.leave_chat(chat_id)
            return

    except ChatAdminRequired:
        await ceger.edit(_("join_7").format(em.gagal, namagece))
        return
    except UserNotParticipant:
        await m.delete()
        return
    except ChannelPrivate:
        await m.delete()
        return
    except Exception as e:
        await ceger.edit(_("err").format(em.gagal, e))
        return


@zb.ubot("leave")
async def _(c: nlx, m, _):
    em = Emojik(c)
    em.initialize()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = initial_ctext(c)
    xenn = await m.reply(_("proses").format(em.proses, proses_))
    no_leave = dB.get_list_from_var(c.me.id, "NO_LEAVE")
    no_leave.append(-1001818398503)
    no_leave.append(-1001537280879)
    if len(m.command) < 2:
        await xenn.edit(_("join_8").format(em.gagal, m.text.split()[0]))
        return
    command = m.text.split(None, 1)[1]
    luci = 0
    nan = 0
    chats = await c.get_chats_dialog(command)
    for chat in chats:
        if chat in no_leave:
            continue
        try:
            chat_info = await c.get_chat_member(chat, "me")
            user_status = chat_info.status
            if user_status not in (
                enums.ChatMemberStatus.OWNER,
                enums.ChatMemberStatus.ADMINISTRATOR,
            ):
                luci += 1
                await c.leave_chat(chat)
        except FloodWait as e:
            await asyncio.sleep(e)
            await c.leave_chat(chat)
            luci += 1
        except Exception:
            nan += 1
    await xenn.delete()
    return await m.reply(
        _("join_6").format(em.sukses, luci, command, em.gagal, nan, command)
    )


@zb.ubot("unleave")
async def _(c: nlx, m, _):
    em = Emojik(c)
    em.initialize()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = initial_ctext(c)
    pp = await m.reply(_("proses").format(em.proses, proses_))
    chat_id = m.command[1] if len(m.command) > 1 else m.chat.id
    blacklist = dB.get_list_from_var(c.me.id, "NO_LEAVE")
    try:
        chat_id = int(chat_id)
    except ValueError:
        return await pp.edit(
            "{}<b>KONTOL KONTOL KALO PAKE NONE PREFIX JANGAN ASAL KETIK GOBLOK\n\n BOT GW YANG EROR ANJ!!!</b>".format(
                em.gagal
            )
        )
    if chat_id in blacklist:
        return await pp.edit(_("spm_9").format(em.sukses))
    dB.add_to_var(c.me.id, "NO_LEAVE", chat_id)
    return await pp.edit(_("spm_8").format(em.sukses, chat_id))


@zb.ubot("addleave")
async def _(c: nlx, m, _):
    em = Emojik(c)
    em.initialize()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = initial_ctext(c)
    pp = await m.reply(_("proses").format(em.proses, proses_))

    blacklist = dB.get_list_from_var(c.me.id, "NO_LEAVE")
    try:
        chat_id = int(m.command[1]) if len(m.command) > 1 else m.chat.id
        if chat_id not in blacklist:
            return await pp.edit(_("spm_10").format(em.gagal, chat_id))
        dB.remove_from_var(c.me.id, "NO_LEAVE", chat_id)
        return await pp.edit(_("spm_11").format(em.gagal, chat_id))

    except Exception as error:
        return await pp.edit(str(error))


@zb.ubot("bl-leave")
async def _(c: nlx, m, _):
    em = Emojik(c)
    em.initialize()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = initial_ctext(c)
    pp = await m.reply(_("proses").format(em.proses, proses_))

    msg = _("spm_12").format(em.sukses)
    listbc = dB.get_list_from_var(c.me.id, "NO_LEAVE", "grup")
    for x in listbc:
        try:
            get = await c.get_chat(x)
            msg += _("gcs_11").format(get.title, get.id)
        except:
            msg += _("gcs_12").format(x)
    await pp.delete()
    return await m.reply(msg)


@zb.ubot("clear-leave")
async def _(c: nlx, m, _):
    em = Emojik(c)
    em.initialize()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = initial_ctext(c)
    msg = await m.reply(_("proses").format(em.proses, proses_))
    get_bls = dB.get_list_from_var(c.me.id, "NO_LEAVE")
    if not get_bls:
        return await msg.edit(_("spm_13").format(em.gagal))
    for x in get_bls:
        dB.remove_from_var(c.me.id, "NO_LEAVE", x)
    return await msg.edit(_("spam_14").format(em.sukses))


@zb.ubot("leavemute")
@zb.deve("leavemute")
async def _(c, m, _):
    em = Emojik(c)
    em.initialize()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = initial_ctext(c)
    xenn = await m.reply_text(_("proses").format(em.proses, proses_))
    luci = 0
    async for dialog in c.get_dialogs():
        if dialog.chat.type in (enums.ChatType.GROUP, enums.ChatType.SUPERGROUP):
            try:
                member = await c.get_chat_member(dialog.chat.id, c.me.id)
                if member.status == enums.ChatMemberStatus.RESTRICTED:
                    luci += 1
                    await c.leave_chat(dialog.chat.id)
            except FloodWait as e:
                await asyncio.sleep(e)
                await c.leave_chat(dialog.chat.id)
                luci += 1
            except Exception:
                continue
    await xenn.delete()
    return await m.reply(
        f"{em.sukses}**Succesfully leaved muted group, succesed: {luci}**"
    )

@zb.ubot("leaveallgc")
async def _(c, m, _):
    em = Emojik(c)
    em.initialize()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = initial_ctext(c)
    xenn = await m.reply_text(_("proses").format(em.proses, proses_))
    luci = 0
    async for dialog in c.get_dialogs():
        if dialog.chat.type in (enums.ChatType.GROUP, enums.ChatType.SUPERGROUP):
            try:
                member = await c.get_chat_member(dialog.chat.id, c.me.id)
                if member.status not in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
                    luci += 1
                    await c.leave_chat(dialog.chat.id)
            except FloodWait as e:
                await asyncio.sleep(e)
                await c.leave_chat(dialog.chat.id)
                luci += 1
            except Exception:
                continue
    await xenn.delete()
    return await m.reply(
        f"{em.sukses}**Succesfully leaved group, succesed: {luci}**"
    )
