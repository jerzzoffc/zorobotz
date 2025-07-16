import os

from pyrogram.enums import StoriesPrivacyRules

from Userbot import nlx
from Userbot.helper.tools import Emojik, initial_ctext, zb, h_s

__MODULES__ = "Story"

def help_string(org):
    return h_s(org, "help_stori")
    

USER_PREMIUM = True


def extract_user_link(link):
    """
    Mengambil (user_identifier, msg_id)
    user_identifier bisa berupa username (tanpa @), atau ID (int)
    """
    try:
        if "t.me/c/" in link:  # link private group
            chat_id = int("-100" + str(link.split("/")[-2]))
            msg_id = int(link.split("/")[-1])
            return chat_id, msg_id
        elif "t.me/" in link:
            # t.me/username/1234 atau t.me/username
            parts = link.replace("https://", "").replace("http://", "").split("/")
            # parts = ['t.me', 'username', '1234'] atau ['t.me', 'username']
            if len(parts) > 2 and parts[2].isdigit():
                username = parts[1]
                msg_id = int(parts[2])
            else:
                username = parts[1] if len(parts) > 1 else ""
                msg_id = None
            username = username.lstrip('@').strip()
            if not username or len(username) < 5:
                return None, msg_id
            return username, msg_id
        else:
            # fallback, kalau bukan link
            username = link.lstrip('@').strip()
            if not username or len(username) < 5:
                return None, None
            return username, None
    except Exception as e:
        print("extract_user_link error:", e)
        return None, None


async def colong_story(g, c: nlx, inf, m):
    msg = m.reply_to_message or m
    text = g.caption or ""

    if g.photo:
        media = await c.download_media(
            g.photo.file_id,
        )
        await c.send_photo(
            m.chat.id,
            media,
            caption=text,
            reply_to_message_id=msg.id,
        )
        await inf.delete()
        os.remove(media)

    elif g.video:
        media = await c.download_media(
            g.video.file_id,
        )
        thumbnail = await c.download_media(g.video.thumbs[-1]) if g.video.thumbs else None
        await c.send_video(
            m.chat.id,
            video=media,
            duration=g.video.duration,
            caption=text,
            thumb=thumbnail,
            reply_to_message_id=msg.id,
        )
        await inf.delete()
        os.remove(media)
        if thumbnail:
            os.remove(thumbnail)
    return


# THANKS TO MY BOROTHER
# NOR SODIKIN


def tomi_send_you_to_hell(m):
    if m.photo:
        return m.photo.file_id
    elif m.video:
        return m.video.file_id
    elif m.animation:
        return m.animation.file_id
    else:
        return None


@zb.ubot("buatstory")
async def _(c: nlx, m, _):
    em = Emojik(c)
    em.initialize()
    rep = m.reply_to_message
    if not rep:
        return await m.reply(
            f"{em.gagal}<b>Balas ke pesan media foto, video, atau animasi yang ada caption-nya.</b>"
        )
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = initial_ctext(c)
    pros = await m.reply(_("proses").format(em.proses, proses_))
    file_id = tomi_send_you_to_hell(rep)
    # Ambil caption persis sesuai pesan yang di-reply (bisa dari caption atau text pada media)
    teks = rep.caption or rep.text or ""
    if not file_id:
        return await pros.edit(_("err").format(em.gagal, "Pesan bukan media yang didukung."))

    # Deteksi otomatis id tujuan story
    if rep.sender_chat:
        tuju_id = rep.sender_chat.id
        tuju_label = rep.sender_chat.title or rep.sender_chat.username or tuju_id
    elif rep.forward_from:
        tuju_id = rep.forward_from.id
        tuju_label = rep.forward_from.first_name or rep.forward_from.username or tuju_id
    elif rep.forward_from_chat:
        tuju_id = rep.forward_from_chat.id
        tuju_label = rep.forward_from_chat.title or rep.forward_from_chat.username or tuju_id
    elif rep.from_user:
        tuju_id = rep.from_user.id
        tuju_label = rep.from_user.first_name or rep.from_user.username or tuju_id
    else:
        tuju_id = "me"
        tuju_label = "akun sendiri"

    try:
        await c.send_story(
            tuju_id, file_id, caption=teks, privacy=StoriesPrivacyRules.PUBLIC
        )
        return await pros.edit(f"{em.sukses}<b>Story berhasil dibuat di {tuju_label}!</b>")
    except Exception as e:
        if "USERNAME_NOT_OCCUPIED" in str(e):
            return await pros.edit(
                f"{em.gagal}<b>Username/ID tujuan tidak ditemukan di Telegram.</b>"
            )
        return await pros.edit(_("err").format(em.gagal, e))


@zb.ubot("cekstory")
async def _(c: nlx, m, _):
    em = Emojik(c)
    em.initialize()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = initial_ctext(c)
    pros = await m.reply(_("proses").format(em.proses, proses_))
    txt = f"{em.sukses}<b>Ini adalah list story lu jink:</b>\n\n"
    async for st in c.get_all_stories():
        st_ = await c.export_story_link("me", st.id)
        txt += f"<b>• ID Story: `{st.id}`\n Tautan Story: <a href='{st_}'>Klik Disini</a></b>"
    await m.reply(txt, disable_web_page_preview=True)
    return await pros.delete()


@zb.ubot("delstory")
async def _(c: nlx, m, _):
    em = Emojik(c)
    em.initialize()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = initial_ctext(c)
    pros = await m.reply(_("proses").format(em.proses, proses_))
    prefix = await c.get_prefix(c.me.id)
    if len(m.command) < 2:
        return await pros.edit(
            "<b>{} Ga gitu lah anj!! Kasih id story lo.\nContoh: `{}delstory` 5\n\nAtau lo bisa ketik `{}cekstory` untuk lihat id story lo!! </b>".format(
                em.gagal, " ".join(prefix[0]), " ".join(prefix[0])
            )
        )
    id_ = m.text.split(None, 1)[1]
    if not id_.isnumeric():
        return await pros.edit(
            f"{em.gagal}<b>Allahu Akbar!! dimana mana id itu angka anj!! bukan huruf atau symbol.</b>"
        )
    await c.delete_stories(story_ids=int(id_))
    return await pros.edit(f"{em.sukses}<b>Mantap story `{id_}` dihapus!!</b>")


@zb.ubot("copystory")
async def _(c: nlx, m, _):
    em = Emojik(c)
    em.initialize()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = initial_ctext(c)
    pros = await m.reply(_("proses").format(em.proses, proses_))
    rep = m.reply_to_message
    if rep:
        link = rep.text or rep.caption
    else:
        if len(m.text.split(None, 1)) > 1:
            link = m.text.split(None, 1)[1]
        else:
            link = ""
    if not link:
        return await pros.edit(
            f"{em.gagal}<b>Kasih link Telegram yang valid!</b>"
        )
    if not link.startswith(("https", "t.me")):
        return await pros.edit(
            f"{em.gagal}<b>Kasih link Telegram, bukan link lain!</b>"
        )
    user, _id = extract_user_link(link)
    if not user:
        return await pros.edit(
            f"{em.gagal}<b>Username/Link tidak valid atau user/channel tidak ditemukan di Telegram.</b>"
        )
    try:
        st = await c.get_stories(user, _id)
    except Exception as e:
        if "USERNAME_NOT_OCCUPIED" in str(e):
            return await pros.edit(f"{em.gagal}<b>Username/link tidak valid atau user/channel tidak ditemukan di Telegram.</b>")
        else:
            return await pros.edit(f"{em.gagal}<b>Error: {e}</b>")
    await colong_story(st, c, pros, m)
    return await pros.delete()
