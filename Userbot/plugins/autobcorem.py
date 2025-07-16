import asyncio
import random

from pyrogram.enums import ChatType
from pyrogram.errors import FloodWait

from config import NO_GCAST
from Userbot.helper.database import dB
from Userbot.helper.tools import Emojik, h_s, initial_ctext, zb
from Userbot.plugins.limit import spam_bot

__MODULES__ = "AutoBcPrem"
USER_PREMIUM = True


def help_string(org):
    return h_s(org, "help_autobcprem")


AB = []
LT = []


def extract_type_and_text(m):
    args = m.text.split(None, 2)
    if len(args) < 2:
        return None, None

    type = args[1]
    msg = (
        m.reply_to_message.text
        if m.reply_to_message
        else args[2] if len(args) > 2 else None
    )
    return type, msg


async def text_autobc(client):
    auto_text_vars = dB.get_var(client.me.id, "AUTO_BC")
    list_ids = []
    list_text = []
    for data in auto_text_vars:
        list_ids.append(int(data["message_id"]))
    for ids in list_ids:
        msg = await client.get_messages("me", ids)
        list_text.append(msg.text)
    return list_text


@zb.ubot("autobc")
async def _(c, m, _):
    em = Emojik(c)
    em.initialize()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = initial_ctext(c)
    msg = await m.reply(_("proses").format(em.proses, proses_))
    type, value = extract_type_and_text(m)
    reply = m.reply_to_message

    logs = "me"
    auto_text_vars = dB.get_var(c.me.id, "AUTO_BC")
    send_msg = []
    if type == "on":
        if not auto_text_vars:
            return await msg.edit(_("aubc_1").format(em.gagal))
        if c.me.id not in AB:
            await msg.edit(_("aubc_2").format(em.sukses))
            AB.append(c.me.id)
            done = 0
            while c.me.id in AB:
                delay = dB.get_var(c.me.id, "DELAY_BC") or 1
                blacklist = dB.get_list_from_var(c.me.id, "BLBC")
                for ax in auto_text_vars:
                    send_msg.append(int(ax["message_id"]))
                txt = random.choice(send_msg)
                msg_id = await c.get_messages(logs, txt)

                group = 0
                async for dialog in c.get_dialogs():
                    if (
                        dialog.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP)
                        and dialog.chat.id not in blacklist
                        and dialog.chat.id not in NO_GCAST
                    ):
                        try:
                            await asyncio.sleep(1)
                            await msg_id.copy(dialog.chat.id)
                            group += 1
                        except FloodWait as e:
                            await asyncio.sleep(e.value)
                            await msg_id.copy(dialog.chat.id)
                            group += 1
                        except Exception:
                            pass

                if c.me.id not in AB:
                    return

                done += 1
                await msg.reply(_("aubc_3").format(em.sukses, done, group, delay))
                await asyncio.sleep(int(60 * int(delay)))
        else:
            return await msg.delete()

    elif type == "off":
        if c.me.id in AB:
            AB.remove(c.me.id)
            return await msg.edit(_("aubc_4").format(em.gagal))
        else:
            return await msg.delete()

    elif type == "add":
        if not reply:
            return await msg.edit(
                f"{em.gagal}<b>Minimal balas teks Tolol, buat pesan nya.</b>"
            )
        await add_auto_text(m)
        return await msg.edit(
            f"{em.sukses}<b>Disimpan untuk pesan AutoBc.</b>",
        )

    elif type == "delay":
        dB.set_var(c.me.id, "DELAY_BC", value)
        return await msg.edit(
            f"{em.sukses}<b>Delay AutoBc diatur ke : <code>{value}</code></b>"
        )

    elif type == "del":
        if not value:
            return await msg.edit(
                f"{em.gagal}<b>Minimal kasih angka Tolol, teks keberapa perlu dihapus.</b>"
            )
        if value == "all":
            dB.set_var(c.me.id, "AUTO_BC", [])
            return await msg.edit(
                f"{em.sukses}<b>Yosh semua teks alay lo udah dihapus.</b>"
            )
        try:
            value = int(value) - 1
            auto_text_vars.pop(value)
            dB.set_var(c.me.id, "AUTO_BC", auto_text_vars)
            return await msg.edit(
                f"{em.sukses}<b>Teks ke : <code>{value+1}</code> dihapus.</b>"
            )
        except Exception as error:
            return await msg.edit(str(error))

    elif type == "get":
        if not auto_text_vars:
            return await msg.edit(f"{em.gagal}<b>Teks AutoBc lo kosong bego.</b>")
        data = await text_autobc(c)
        txt = "<b>Teks AutoBc Alay Lo</b>\n\n"
        for num, x in enumerate(data, 1):
            txt += f"{num}: {x}\n\n"

        return await msg.edit(txt)

    elif type == "limit":
        if value == "off":
            if c.me.id in LT:
                LT.remove(c.me.id)
                return await msg.edit(f"{em.gagal}<b>Auto Limit dimatikan.</b>")
            else:
                return await msg.delete()

        elif value == "on":
            if c.me.id not in LT:
                LT.append(c.me.id)
                await msg.edit(f"{em.sukses}<b>Auto Limit dihidupkan.</b>")
                while c.me.id in LT:
                    for x in range(2):
                        await spam_bot(c, m, _)
                        await asyncio.sleep(5)
                    await asyncio.sleep(1200)
            else:
                return await msg.delete()
        else:
            return await msg.edit(
                f"{em.gagal}<b>Salah Goblok!! Minimal baca perintah bantuan lah.</b>"
            )
    else:
        return await msg.edit(
            f"{em.gagal}<b>Salah Goblok!! Minimal baca perintah bantuan lah.</b>"
        )
    return


async def add_auto_text(m):
    c = m._client
    auto_text = dB.get_var(c.me.id, "AUTO_BC") or []
    rep = m.reply_to_message
    value = None

    logs = "me"
    type_mapping = {
        "text": rep.text,
        "photo": rep.photo,
        "voice": rep.voice,
        "audio": rep.audio,
        "video": rep.video,
        "video_note": rep.video_note,
        "animation": rep.animation,
        "sticker": rep.sticker,
        "document": rep.document,
        "contact": rep.contact,
    }
    for media_type, media in type_mapping.items():
        if media:
            send = await rep.copy(logs)
            value = {
                "type": media_type,
                "message_id": send.id,
            }
            break
    if value:
        auto_text.append(value)
        dB.set_var(c.me.id, "AUTO_BC", auto_text)
