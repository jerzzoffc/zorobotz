import asyncio
import random

from pyrogram.enums import ChatType
from pyrogram.errors import FloodWait

from config import NO_GCAST
from Userbot.helper.database import dB
from Userbot.helper.tools import Emojik, h_s, initial_ctext, zb
from Userbot.plugins.limit import spam_bot

__MODULES__ = "AutoGcPrem"
USER_PREMIUM = True


def help_string(org):
    return h_s(org, "help_augcs")

def emoji(alias):
    emojis = {
        "AKT": "<emoji id=4916036072560919511>✅</emoji>",

        "NOTAKT": "<emoji id=4918014360267260850>⛔️</emoji>",
    }
    return emojis.get(alias, "🕸")


akt = emoji("AKT")
notakt = emoji("NOTAKT")


AG = []
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


async def text_autogcast(client):
    auto_text_vars = dB.get_var(client.me.id, "AUTO_GCAST")
    list_ids = []
    list_text = []
    for data in auto_text_vars:
        list_ids.append(int(data["message_id"]))
    for ids in list_ids:
        msg = await client.get_messages("me", ids)
        list_text.append(msg.text)
    return list_text

status_autogcast = {}

@zb.ubot("autogc")
async def _(c, m, _):
    em = Emojik(c)
    em.initialize()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = initial_ctext(c)
    msg = await m.reply(_("proses").format(em.proses, proses_))
    type, value = extract_type_and_text(m)
    reply = m.reply_to_message

    logs = "me"
    auto_text_vars = dB.get_var(c.me.id, "AUTO_GCAST")
    send_msg = []
    
    def clean_status(user_id):
        if user_id in status_autogcast and not status_autogcast[user_id]:
            del status_autogcast[user_id]

    if type == "on":
        if not auto_text_vars:
            return await msg.edit(_("augcs_1").format(em.gagal))
        if c.me.id not in AG:
            await msg.edit(_("augcs_2").format(em.sukses))
            AG.append(c.me.id)
            done, failed = 0, 0
            rotate = dB.get_var(c.me.id, "ROTATE") or 999 * 999 * 999
            status_autogcast[c.me.id] = False
            while c.me.id in AG:
                if rotate == done:
                    AG.remove(c.me.id)
                    clean_status(c.me.id)
                    return await msg.edit(f"Limit putaran tercapai, menghentikan autogcast.")
                
                delay = dB.get_var(c.me.id, "DELAY_GCAST") or 1
                blacklist = dB.get_list_from_var(c.me.id, "BLGCAST")
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
                            failed += 1

                if c.me.id not in AG:
                    clean_status(c.me.id)
                    return

                done += 1
                await msg.reply(_("augcs_3").format(done, group, failed, delay))
                await asyncio.sleep(int(60 * int(delay)))
        else:
            return await msg.delete()

    elif type == "status":
        status = status_autogcast.get(c.me.id, False)
        text = f"{akt} autogcast sedang berjalan" if status == "True" else f"{notakt} autogcast tidak diaktifkan"
        return await msg.edit(text)

    elif type == "off":
        if c.me.id in AG:
            AG.remove(c.me.id)
            clean_status(c.me.id)
            return await msg.edit(_("augcs_4").format(em.gagal))
        else:
            return await msg.delete()

    elif type == "rotate":
        try:
            num = int(value)
            dB.set_var(c.me.id, "ROTATE", num)
            return await msg.edit(f"{em.sukses} Putaran autogcast berhasil di settings ke {num}")
        except Exception as e:
            return await msg.edit(str(e))

    elif type == "add":
        if not reply:
            return await msg.edit(
                f"{em.gagal}<b>Minimal balas teks Tolol, buat pesan nya.</b>"
            )
        await add_auto_text(m)
        return await msg.edit(
            f"{em.sukses}<b>Disimpan untuk pesan Auto Gcast Premium.</b>",
        )

    elif type == "delay":
        dB.set_var(c.me.id, "DELAY_GCAST", value)
        return await msg.edit(
            f"{em.sukses}<b>Delay Auto Gcast Premium diatur ke : <code>{value}</code></b>"
        )

    elif type == "del":
        if not value:
            return await msg.edit(
                f"{em.gagal}<b>Minimal kasih angka Tolol, teks keberapa perlu dihapus.</b>"
            )
        if value == "all":
            dB.set_var(c.me.id, "AUTO_GCAST", [])
            return await msg.edit(
                f"{em.sukses}<b>Yosh semua teks alay lo udah dihapus.</b>"
            )
        try:
            value = int(value) - 1
            auto_text_vars.pop(value)
            dB.set_var(c.me.id, "AUTO_GCAST", auto_text_vars)
            return await msg.edit(
                f"{em.sukses}<b>Teks ke : <code>{value+1}</code> dihapus.</b>"
            )
        except Exception as error:
            return await msg.edit(str(error))

    elif type == "get":
        if not auto_text_vars:
            return await msg.edit(f"{em.gagal}<b>Teks Auto Gcast Premium lo kosong bego.</b>")
        data = await text_autogcast(c)
        txt = "<b>Teks Gcast Premium Alay Lo</b>\n\n"
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
    auto_text = dB.get_var(c.me.id, "AUTO_GCAST") or []
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
        dB.set_var(c.me.id, "AUTO_GCAST", auto_text)
