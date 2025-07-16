import asyncio
from datetime import datetime
import pytz
import os

from Userbot.helper.tools import Emojik, zb, h_s
from Userbot import nlx, bot
from Userbot.helper.database import dB
from pyrogram.enums import ChatType
from pyrogram.types import Message
from pyrogram.errors import MessageDeleteForbidden
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import ChatMemberUpdated

__MODULES__ = "WelcomePremiumBot"

WELCOME_GROUPS_KEY = "WELCOME_BOT_GROUPS"
WELCOME_MEDIA_KEY = "WELCOME_BOT_MEDIA"
WELCOME_TEXT_KEY = "WELCOME_BOT_TEXT"
WELCOME_GROUPS_LIST_KEY = "WELCOME_BOT_GROUPS_LIST"

# ========== PENYIMPANAN GLOBAL UNTUK TEXT & MEDIA ==========
# Text dan media berlaku untuk semua grup welcome untuk tiap client/user

def get_welcome_media_global(c):
    return dB.get_var(c.me.id, WELCOME_MEDIA_KEY, "WELCOME_BOT") or None

def set_welcome_media_global(c, media):
    dB.set_var(c.me.id, WELCOME_MEDIA_KEY, media, "WELCOME_BOT")

def get_welcome_text_global(c):
    return dB.get_var(c.me.id, WELCOME_TEXT_KEY, "WELCOME_BOT") or None

def set_welcome_text_global(c, text):
    dB.set_var(c.me.id, WELCOME_TEXT_KEY, text, "WELCOME_BOT")

def del_welcome_text_global(c):
    # Reset ke default, tidak hapus media
    default_text = (
        "• Nama: <b>{first} {last}</b>\n"
        "• Username: {username}\n"
        "• UserID: <code>{userid}</code>\n"
        "• Grup: <b>{group}</b>\n"
        "• Owner: {owner}\n"
        "• Member ke: {badge}\n"
        "• Waktu join: {waktu}\n"
    )
    set_welcome_text_global(c, default_text)

def get_welcome_status(c):
    return dB.get_var(c.me.id, WELCOME_GROUPS_KEY, "WELCOME_BOT") or {}

def set_welcome_status(c, group_id, status, group_name):
    status_dict = get_welcome_status(c)
    status_dict[str(group_id)] = {
        "name": group_name,
        "status": status
    }
    dB.set_var(c.me.id, WELCOME_GROUPS_KEY, status_dict, "WELCOME_BOT")

def get_welcome_groups_list(c):
    return dB.get_var(c.me.id, WELCOME_GROUPS_LIST_KEY, "WELCOME_BOT") or []

def set_welcome_groups_list(c, groups):
    dB.set_var(c.me.id, WELCOME_GROUPS_LIST_KEY, groups, "WELCOME_BOT")

def parse_template(text, user, group_name, group_id, owner, badge, tz_jakarta_time):
    # Tag/mention user yang join
    if hasattr(user, "mention") and callable(user.mention):
        user_mention = user.mention()
    elif hasattr(user, "mention"):
        user_mention = user.mention
    else:
        user_mention = f"<a href='tg://user?id={user.id}'>{user.first_name or user.id}</a>"

    # Username user join (mention/tag)
    if user.username:
        username_mention = f"@{user.username}"
    else:
        username_mention = user_mention

    # Tag/mention owner group
    if owner:
        if hasattr(owner, "mention") and callable(owner.mention):
            owner_mention = owner.mention()
        elif hasattr(owner, "mention"):
            owner_mention = owner.mention
        else:
            owner_mention = f"<a href='tg://user?id={owner.id}'>{owner.first_name or owner.id}</a>"
        if hasattr(owner, "username") and owner.username:
            owner_username = f"@{owner.username}"
        else:
            owner_username = owner_mention
    else:
        owner_mention = "Unknown"
        owner_username = "Unknown"

    first = user.first_name or ""
    last = user.last_name or ""
    fullname = (user.first_name or "") + (" " + user.last_name if user.last_name else "")
    template_vars = {
        "{mention}": user_mention,  # Tag/mention user join
        "{first}": first,
        "{last}": last,
        "{fullname}": fullname,
        "{username}": username_mention,  # Tag/mention user join
        "{userid}": f"{user.id}",
        "{group}": group_name,
        "{groupid}": f"{group_id}",
        "{owner}": owner_mention,  # Tag/mention owner group
        "{ownerusername}": owner_username,  # Tag/mention owner group
        "{badge}": badge,
        "{waktu}": tz_jakarta_time,
    }
    for k, v in template_vars.items():
        text = text.replace(k, v)
    return text

@zb.ubot("addwelc")
async def cmd_addwelc(c: nlx, m: Message, _):
    em = Emojik(c)
    em.initialize()
    if not m.chat or m.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return await m.reply("❌ <b>Perintah ini hanya di grup!</b>", quote=True)
    groups = get_welcome_groups_list(c)
    if m.chat.id not in groups:
        groups.append(m.chat.id)
        set_welcome_groups_list(c, groups)
        await m.reply(
            "<blockquote>✅ Grup ini berhasil ditambahkan ke daftar Welcome Group.</blockquote>", quote=True)
    else:
        await m.reply(
            "<blockquote>❌ Grup ini sudah ada di daftar Welcome Group.</blockquote>", quote=True)

@zb.ubot("delwelc")
async def cmd_delwelc(c: nlx, m: Message, _):
    em = Emojik(c)
    em.initialize()
    groups = get_welcome_groups_list(c)
    if m.chat.id in groups:
        groups.remove(m.chat.id)
        set_welcome_groups_list(c, groups)
        await m.reply(
            "<blockquote>✅ Grup ini berhasil dihapus dari daftar Welcome Group.</blockquote>", quote=True)
    else:
        await m.reply(
            "<blockquote>❌ Grup ini tidak ada di daftar Welcome Group.</blockquote>", quote=True)

@zb.ubot("listwelc")
async def cmd_listwelc(c: nlx, m: Message, _):
    em = Emojik(c)
    em.initialize()
    groups = get_welcome_groups_list(c)
    if not groups:
        return await m.reply("<blockquote>❗️ Daftar Welcome Group kosong.</blockquote>", quote=True)
    text = "<b>Daftar Grup Welcome :</b>\n\n"
    for gid in groups:
        try:
            chat = await c.get_chat(gid)
            text += f"<code>{gid}</code> - {chat.title}\n"
        except Exception:
            text += f"<code>{gid}</code>\n"
    await m.reply(f"<blockquote>{text}</blockquote>", quote=True)

@zb.ubot("welcomebot")
async def cmd_welcomebot(c: nlx, m: Message, _):
    em = Emojik(c)
    em.initialize()
    args = c.get_arg(m)
    group_list = get_welcome_groups_list(c)
    if args == "help":
        help_text = (
            "<b>WelcomeBot - Bantuan & Petunjuk</b>\n\n"
            "• <code>.addwelc</code>: Tambahkan grup ke daftar WelcomeBot.\n"
            "• <code>.delwelc</code>: Hapus grup dari daftar WelcomeBot.\n"
            "• <code>.listwelc</code>: Lihat daftar grup WelcomeBot.\n"
            "• <code>.welcomebot on/off/status</code>: Aktifkan/Nonaktifkan WelcomeBot atau lihat status semua grup.\n"
            "• <code>.welcomebot help</code>: Tampilkan bantuan ini.\n"
            "• <code>/welcomepict</code>: (Balas media ke bot utama) set welcome media global (foto/video/gif/sticker).\n"
            "• <code>.setwelcome</code>: (Balas text) set pesan welcome global (support variable).\n"
            "• <code>.delwelcometext</code>: Reset pesan welcome ke default (tidak menghapus media).\n"
            "\n"
            "<u>Template variable:</u>\n"
            "<code>{mention}</code>, <code>{fullname}</code>, <code>{userid}</code>, <code>{username}</code>, <code>{group}</code>, <code>{owner}</code>, <code>{badge}</code>, <code>{waktu}</code>\n"
            "\n"
            "Media & pesan welcome berlaku untuk semua grup yang terdaftar WelcomeBot.\n"
            "WelcomeBot juga support grup privat/approval join.\n"
        )
        return await m.reply(f"<blockquote>{help_text}</blockquote>", quote=True)
    if args not in ["on", "off", "status"]:
        return await m.reply("<blockquote>❌ Gunakan: <code>.welcomebot on/off/status/help</code></blockquote>", quote=True)
    if args in ["on", "off"]:
        if not group_list:
            return await m.reply("<blockquote>❗️ Tidak ada grup di daftar Welcome Group. Gunakan <code>.addwelc</code> di grup.</blockquote>", quote=True)
        for gid in group_list:
            try:
                chat = await c.get_chat(gid)
                set_welcome_status(c, gid, args, chat.title)
            except Exception:
                set_welcome_status(c, gid, args, str(gid))
        emoji = "✅" if args == "on" else "❌"
        await m.reply(
            f"<blockquote>{emoji} WelcomeBot telah <b>{args.upper()}</b> untuk semua grup di daftar Welcome Group ({len(group_list)} grup).</blockquote>",
            quote=True
        )
    else:
        status_dict = get_welcome_status(c)
        if not group_list:
            return await m.reply("<blockquote>❗️ Tidak ada grup di daftar Welcome Group.</blockquote>", quote=True)
        text = "<b>Status WelcomeBot Grup (daftar Welcome Group):</b>\n\n"
        for gid in group_list:
            v = status_dict.get(str(gid))
            if not v:
                try:
                    chat = await c.get_chat(gid)
                    group_name = chat.title
                except Exception:
                    group_name = str(gid)
                stat = "❌"
                stat_txt = "OFF"
            else:
                group_name = v["name"]
                stat = "✅" if v["status"] == "on" else "❌"
                stat_txt = v["status"].upper()
            text += f"<b>{group_name}</b> <code>{gid}</code> {stat} ({stat_txt})\n"
        await m.reply(f"<blockquote>{text}</blockquote>", quote=True)

@bot.on_message(filters.command("welcomepict") & filters.reply)
async def set_media_welcome(bot, message):
    reply = message.reply_to_message
    group_id = message.chat.id

    is_video_doc = (
        reply.document and
        reply.document.mime_type and
        reply.document.mime_type.startswith("video/")
    )
    is_gif_doc = (
        reply.document and
        reply.document.mime_type and
        reply.document.mime_type == "image/gif"
    )
    is_sticker = reply.sticker is not None

    if not (reply.photo or reply.video or reply.animation or is_video_doc or is_gif_doc or is_sticker):
        return await message.reply(
            "<blockquote>❌ Reply ke foto, video (.mp4), GIF, atau sticker untuk set welcome media.</blockquote>")

    sent_msg = None
    media_type = None
    file_path = None

    try:
        if reply.photo:
            file_path = await reply.download()
            sent_msg = await bot.send_photo(group_id, file_path)
            media_type = "photo"
        elif reply.video:
            file_path = await reply.download()
            sent_msg = await bot.send_video(group_id, file_path)
            media_type = "video"
        elif reply.animation:
            file_path = await reply.download()
            sent_msg = await bot.send_animation(group_id, file_path)
            media_type = "gif"
        elif is_video_doc or is_gif_doc:
            file_path = await reply.download()
            mime = reply.document.mime_type
            if mime == "image/gif":
                sent_msg = await bot.send_animation(group_id, file_path)
                media_type = "gif"
            else:
                sent_msg = await bot.send_video(group_id, file_path)
                media_type = "video"
        elif is_sticker:
            sent_msg = await bot.send_sticker(group_id, reply.sticker.file_id)
            media_type = "sticker"
        else:
            return await message.reply("<blockquote>❌ Media tidak didukung.</blockquote>")
    finally:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

    try:
        await sent_msg.delete()
    except Exception:
        pass

    if not sent_msg:
        return await message.reply("<blockquote>❌ Gagal upload media.</blockquote>")

    if media_type == "photo":
        file_id = sent_msg.photo.file_id
    elif media_type == "video":
        file_id = sent_msg.video.file_id
    elif media_type == "gif":
        file_id = sent_msg.animation.file_id
    elif media_type == "sticker":
        file_id = sent_msg.sticker.file_id
    else:
        return await message.reply("<blockquote>❌ Tidak bisa ambil file_id.</blockquote>")

    set_welcome_media_global(bot, {"type": media_type, "file_id": file_id})
    await message.reply(f"<blockquote>✅ Welcome media berhasil disimpan (global untuk semua grup)!</blockquote>")

@zb.ubot("setwelcome")
async def cmd_setwelcomebot(c: nlx, m: Message, _):
    em = Emojik(c)
    em.initialize()
    if not m.reply_to_message or not m.reply_to_message.text:
        return await m.reply("<blockquote>❌ Balas ke pesan text yang ingin dijadikan pesan welcome. Support variable, badge, waktu, dst.</blockquote>", quote=True)
    text = m.reply_to_message.text
    set_welcome_text_global(c, text)
    await m.reply(
        "<blockquote>✅ Pesan welcome bot berhasil disimpan (global untuk semua grup)!\n\n<br>Support variable:\n{mention} {first} {username} {fullname} {userid} {group} {groupid} {owner} {badge} {waktu}</blockquote>", 
        quote=True
    )

@zb.ubot("delwelcometext")
async def cmd_delwelcomebot(c: nlx, m: Message, _):
    em = Emojik(c)
    em.initialize()
    del_welcome_text_global(c)
    await m.reply("<blockquote>✅ Pesan welcome berhasil direset ke default! (media tetap tersimpan)</blockquote>", quote=True)

@zb.ubot("welcome")
async def help_welcomebot_cmd(c: nlx, m: Message, _):
    text = (
        "<b>Plugin WelcomeBot (Notif oleh bot utama)</b>\n\n"
        "<u>Fitur Premium:</u>\n"
        "• Welcome otomatis oleh bot utama saat ada member join.\n"
        "• Support media (foto/video/GIF/sticker via file_id Telegram) dan template variable.\n"
        "• Badge/level: Member ke-X (otomatis), waktu join (WIB).\n"
        "• Auto blokir user yang keluar dari grup (langsung banned).\n"
        "\n<u>Perintah:</u>\n"
        "<code>.addwelc</code> - Tambah grup ke daftar Welcome\n"
        "<code>.delwelc</code> - Hapus grup dari daftar Welcome\n"
        "<code>.listwelc</code> - List grup Welcome\n"
        "<code>.welcomebot on/off/status/help</code> - Aktif/nonaktifkan welcome seluruh grup di daftar, lihat bantuan\n"
        "<code>/welcomepict</code> (reply media, ke bot utama) - Set media welcome (foto/video/gif/sticker WAJIB via bot utama)\n"
        "<code>.setwelcome</code> (balas text) - Set pesan welcome (support variable, berlaku global)\n"
        "<code>.delwelcometext</code> - Reset pesan ke default (tidak menghapus media)\n"
        "\n<u>Template variable:</u>\n"
        "<code>{mention}</code>=mention user, <code>{fullname}</code>=nama, <code>{userid}</code>=ID user\n"
        "<code>{group}</code>=nama grup, <code>{owner}</code>=owner grup, <code>{badge}</code>=badge ke-X\n"
        "<code>{waktu}</code>=waktu join (WIB)\n"
        "\nContoh di .setwelcome (balas pesan):\n"
        "<code>Selamat datang {mention} di {group}!\nKamu adalah member ke-{badge}.\nWaktu join: {waktu}</code>\n"
        "\n<b>NB:</b> Bot utama harus sudah join & admin di grup.\n"
        "Media dan pesan welcome berlaku untuk semua grup WelcomeBot, termasuk grup privat/approval join."
    )
    await m.reply(f"<blockquote>{text}</blockquote>", quote=True)

@nlx.on_message(filters.new_chat_members, group=112)
async def welcome_new_member_bot(client, message: Message):
    group_id = message.chat.id
    group_name = message.chat.title

    group_list = get_welcome_groups_list(client)
    if group_id not in group_list:
        return

    status_dict = get_welcome_status(client)
    group_stat = status_dict.get(str(group_id), {})
    if group_stat.get("status") != "on":
        return

    media = get_welcome_media_global(bot)
    text_template = get_welcome_text_global(client)

    owner = None
    try:
        admins = await client.get_chat_administrators(group_id)
        for adm in admins:
            if adm.status == "creator":
                owner = adm.user
                break
    except Exception:
        pass

    try:
        group = await bot.get_chat(group_id)
        member_count = group.members_count or 0
    except Exception:
        member_count = 0

    now_jakarta = datetime.now(pytz.timezone("Asia/Jakarta"))
    waktu_jakarta_str = now_jakarta.strftime("%d-%m-%Y %H:%M:%S WIB")

    for user in message.new_chat_members:
        user_photo_id = None
        try:
            photos = await client.get_profile_photos(user.id, limit=1)
            if photos.total_count > 0:
                user_photo_id = photos.photos[0].file_id
        except Exception:
            pass

        badge = f"👑 {member_count}" if member_count else "👑 -"
        if text_template:
            text_detail = parse_template(
                text_template, user, group_name, group_id, owner, badge, waktu_jakarta_str
            )
        else:
            username = f"@{user.username}" if user.username else "-"
            owner_mention = owner.mention if owner else "Unknown"
            text_detail = (
                f"• Nama: <b>{user.first_name} {user.last_name or ''}</b>\n"
                f"• Username: {username}\n"
                f"• UserID: <code>{user.id}</code>\n"
                f"• Grup: <b>{group_name}</b>\n"
                f"• Owner: {owner_mention}\n"
                f"• Member ke: {badge}\n"
                f"• Waktu join: {waktu_jakarta_str}\n"
            )
        try:
            if media and "file_id" in media:
                if media["type"] == "photo":
                    await bot.send_photo(group_id, media["file_id"], caption=f"<blockquote>{text_detail}</blockquote>")
                elif media["type"] == "video":
                    await bot.send_video(group_id, media["file_id"], caption=f"<blockquote>{text_detail}</blockquote>")
                elif media["type"] == "gif":
                    await bot.send_animation(group_id, media["file_id"], caption=f"<blockquote>{text_detail}</blockquote>")
                elif media["type"] == "sticker":
                    await bot.send_sticker(group_id, media["file_id"])
                    await bot.send_message(group_id, f"<blockquote>{text_detail}</blockquote>")
                else:
                    await bot.send_message(group_id, f"<blockquote>{text_detail}</blockquote>")
            elif user_photo_id:
                await bot.send_photo(group_id, user_photo_id, caption=f"<blockquote>{text_detail}</blockquote>")
            else:
                await bot.send_message(group_id, f"<blockquote>{text_detail}</blockquote>")
        except Exception as e:
            await bot.send_message(group_id, f"<blockquote>❌ Gagal kirim welcome: {e}</blockquote>")

@nlx.on_chat_member_updated(group=114)
async def welcome_approved_member(client, chat_member_updated: ChatMemberUpdated):
    old_status = chat_member_updated.old_chat_member.status
    new_status = chat_member_updated.new_chat_member.status
    if (
        old_status in [ChatMemberStatus.RESTRICTED, ChatMemberStatus.LEFT] and
        new_status == ChatMemberStatus.MEMBER
    ):
        group_id = chat_member_updated.chat.id
        group_name = chat_member_updated.chat.title
        group_list = get_welcome_groups_list(client)
        if group_id not in group_list:
            return

        status_dict = get_welcome_status(client)
        group_stat = status_dict.get(str(group_id), {})
        if group_stat.get("status") != "on":
            return

        media = get_welcome_media_global(bot)
        text_template = get_welcome_text_global(client)

        owner = None
        try:
            admins = await client.get_chat_administrators(group_id)
            for adm in admins:
                if adm.status == "creator":
                    owner = adm.user
                    break
        except Exception:
            pass

        try:
            group = await bot.get_chat(group_id)
            member_count = group.members_count or 0
        except Exception:
            member_count = 0

        from datetime import datetime
        import pytz
        now_jakarta = datetime.now(pytz.timezone("Asia/Jakarta"))
        waktu_jakarta_str = now_jakarta.strftime("%d-%m-%Y %H:%M:%S WIB")

        user = chat_member_updated.new_chat_member.user
        user_photo_id = None
        try:
            photos = await client.get_profile_photos(user.id, limit=1)
            if photos.total_count > 0:
                user_photo_id = photos.photos[0].file_id
        except Exception:
            pass

        badge = f"👑 {member_count}" if member_count else "👑 -"
        if text_template:
            text_detail = parse_template(
                text_template, user, group_name, group_id, owner, badge, waktu_jakarta_str
            )
        else:
            username = f"@{user.username}" if user.username else "-"
            owner_mention = owner.mention if owner else "Unknown"
            text_detail = (
                f"• Nama: <b>{user.first_name} {user.last_name or ''}</b>\n"
                f"• Username: {username}\n"
                f"• UserID: <code>{user.id}</code>\n"
                f"• Grup: <b>{group_name}</b>\n"
                f"• Owner: {owner_mention}\n"
                f"• Member ke: {badge}\n"
                f"• Waktu join: {waktu_jakarta_str}\n"
            )
        try:
            if media and "file_id" in media:
                if media["type"] == "photo":
                    await bot.send_photo(group_id, media["file_id"], caption=f"<blockquote>{text_detail}</blockquote>")
                elif media["type"] == "video":
                    await bot.send_video(group_id, media["file_id"], caption=f"<blockquote>{text_detail}</blockquote>")
                elif media["type"] == "gif":
                    await bot.send_animation(group_id, media["file_id"], caption=f"<blockquote>{text_detail}</blockquote>")
                elif media["type"] == "sticker":
                    await bot.send_sticker(group_id, media["file_id"])
                    await bot.send_message(group_id, f"<blockquote>{text_detail}</blockquote>")
                else:
                    await bot.send_message(group_id, f"<blockquote>{text_detail}</blockquote>")
            elif user_photo_id:
                await bot.send_photo(group_id, user_photo_id, caption=f"<blockquote>{text_detail}</blockquote>")
            else:
                await bot.send_message(group_id, f"<blockquote>{text_detail}</blockquote>")
        except Exception as e:
            await bot.send_message(group_id, f"<blockquote>❌ Gagal kirim welcome: {e}</blockquote>")

@nlx.on_message(filters.left_chat_member, group=113)
async def auto_block_exit(client, message: Message):
    group_id = message.chat.id
    group_list = get_welcome_groups_list(client)
    if group_id not in group_list:
        return
    user = message.left_chat_member
    try:
        await bot.ban_chat_member(group_id, user.id)
        await bot.send_message(group_id, f"<blockquote>👋 <b>{user.mention} telah keluar\nOtomatis diblokir (ban) dari grup.</b></blockquote>")
    except Exception as e:
        await bot.send_message(group_id, f"<blockquote>❌ Gagal blokir {user.mention}: {e}</blockquote>")
