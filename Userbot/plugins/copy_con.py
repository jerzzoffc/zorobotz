import os
import time
import asyncio
from time import time

from Userbot import bot, nlx
from Userbot.helper.tools import Emojik, h_s, initial_ctext, zb, progress

__MODULES__ = "Content"
USER_PREMIUM = True

def help_string(org):
    return h_s(org, "help_content")

COPY_ID = {}

nyolong_jalan = False

async def gas_download(g, c: nlx, inf, m):
    text = g.caption or ""

    if g.photo:
        media = await c.download_media(
            g,
            progress=progress,
            progress_args=(
                inf,
                time(),
                "Download Photo",
                g.photo.file_id,
            ),
        )
        await c.send_photo(
            m.chat.id,
            media,
            caption=text
        )
        await inf.delete()
        os.remove(media)

    elif g.animation:
        media = await c.download_media(
            g,
            progress=progress,
            progress_args=(
                inf,
                time(),
                "Download Animation",
                g.animation.file_id,
            ),
        )
        await c.send_animation(
            m.chat.id,
            animation=media,
            caption=text
        )
        await inf.delete()
        os.remove(media)

    elif g.voice:
        media = await c.download_media(
            g,
            progress=progress,
            progress_args=(inf, time(), "Download Voice", g.voice.file_id),
        )
        await c.send_voice(
            m.chat.id,
            voice=media,
            caption=text
        )
        await inf.delete()
        os.remove(media)

    elif g.audio:
        media = await c.download_media(
            g,
            progress=progress,
            progress_args=(
                inf,
                time(),
                "Download Audio",
                g.audio.file_id,
            ),
        )
        thumbnail = await c.download_media(g.audio.thumbs[-1]) or None
        await c.send_audio(
            m.chat.id,
            audio=media,
            duration=g.audio.duration,
            caption=text,
            thumb=thumbnail
        )
        await inf.delete()
        os.remove(media)
        if thumbnail:
            os.remove(thumbnail)

    elif g.document:
        media = await c.download_media(
            g,
            progress=progress,
            progress_args=(
                inf,
                time(),
                "Download Document",
                g.document.file_id,
            ),
        )
        await c.send_document(
            m.chat.id,
            document=media,
            caption=text
        )
        await inf.delete()
        os.remove(media)

    elif g.video:
        media = await c.download_media(
            g,
            progress=progress,
            progress_args=(
                inf,
                time(),
                "Download Video",
                g.video.file_name,
            ),
        )
        thumbnail = await c.download_media(g.video.thumbs[-1]) or None
        await c.send_video(
            m.chat.id,
            video=media,
            duration=g.video.duration,
            caption=text,
            thumb=thumbnail
        )
        await inf.delete()
        os.remove(media)
        if thumbnail:
            os.remove(thumbnail)

@zb.ubot("copy")
async def _(c: nlx, m, _):
    em = Emojik(c)
    em.initialize()
    msg = m.reply_to_message or m
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = initial_ctext(c)
    inf = await m.reply(_("proses").format(em.proses, proses_))
    links = c.get_arg(m)
    if not links:
        return await inf.edit(_("cpy_1").format(em.gagal, m.command))
    
    link_list = [l.strip() for l in links.split(",") if l.strip()]
    if not link_list:
        return await inf.edit(_("cpy_1").format(em.gagal, m.command))
    total = 0
    failed = 0
    for link in link_list:
        if "?single" in link:
            link = link.replace("?single", "")
        if link.startswith(("https", "t.me")):
            try:
                msg_id = int(link.split("/")[-1])
                if "t.me/c/" in link:
                    chat = int("-100" + str(link.split("/")[-2]))
                    try:
                        g = await c.get_messages(chat, msg_id)
                        try:
                            await g.copy(m.chat.id)
                            total += 1
                        except Exception:
                            try:
                                await gas_download(g, c, inf, m)
                                total += 1
                            except Exception:
                                failed += 1
                    except Exception:
                        failed += 1
                else:
                    chat = str(link.split("/")[-2])
                    try:
                        got = await c.get_messages(chat, msg_id)
                        await got.copy(m.chat.id)
                        total += 1
                    except Exception:
                        try:
                            text = f"get_msg_copy {id(m)}"
                            x = await c.get_inline_bot_results(bot.me.username, text)
                            results = await c.send_inline_bot_result(
                                m.chat.id,
                                x.query_id,
                                x.results[0].id
                            )
                            COPY_ID[c.me.id] = int(results.updates[0].id)
                            total += 1
                        except Exception:
                            failed += 1
            except Exception:
                failed += 1
        else:
            failed += 1
        await asyncio.sleep(1)
    # Notifikasi akhir SELALU tampil
    await inf.edit(f"<emoji id=5260416304224936047>✅</emoji> <b>Berhasil copy {total} pesan dari {len(link_list)} link.</b>\n<emoji id=5260342697075416641>❌</emoji> Gagal: {failed} link.")
