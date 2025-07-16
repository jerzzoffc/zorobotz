import asyncio
from pyrogram.enums import ChatType
from pyrogram.types import Message, ChatInviteLink
from Userbot.helper.database import dB
from Userbot.helper.tools import Emojik, zb
from Userbot import nlx, bot
from pyrogram import filters
from pyrogram.helpers import ikb
from config import log_autoreply  # hanya fallback jika masih mau dipakai
from Userbot.helper.tools import h_s, initial_ctext

__MODULES__ = "AutoReply"

def help_string(org):
    return h_s(org, "help_autoreply")


# ================================ NON-TOPIC (lama) ================================#@moire_mor
def get_autoreply_status(uid):
    return dB.get_var(uid, "AUTOREPLY_STATUS") or False

def set_autoreply_status(uid, value):
    dB.set_var(uid, "AUTOREPLY_STATUS", value)

def get_autoreply_groups(uid):
    return dB.get_var(uid, "AUTOREPLY_GROUPS") or []

def set_autoreply_groups(uid, groups):
    dB.set_var(uid, "AUTOREPLY_GROUPS", groups)

def get_keywords(uid):
    return dB.get_var(uid, "AUTOREPLY_KEYWORDS") or []

def set_keywords(uid, keywords):
    dB.set_var(uid, "AUTOREPLY_KEYWORDS", keywords)

def get_responses(uid):
    return dB.get_var(uid, "AUTOREPLY_RESPONSES") or []

def set_responses(uid, responses):
    dB.set_var(uid, "AUTOREPLY_RESPONSES", responses)

def get_log_group(uid):
    return dB.get_var(uid, "AUTOREPLY_LOG_GROUP")

def set_log_group(uid, group_id):
    dB.set_var(uid, "AUTOREPLY_LOG_GROUP", group_id)

# ================================ TOPIC (baru) ================================
def get_topic_status(uid):
    return dB.get_var(uid, "AUTOREPLY_TOPIC_STATUS") or False

def set_topic_status(uid, value):
    dB.set_var(uid, "AUTOREPLY_TOPIC_STATUS", value)

def get_topic_groups(uid):
    return dB.get_var(uid, "AUTOREPLY_TOPIC_GROUPS") or []

def set_topic_groups(uid, groups):
    dB.set_var(uid, "AUTOREPLY_TOPIC_GROUPS", groups)

def get_topic_keywords(uid):
    return dB.get_var(uid, "AUTOREPLY_TOPIC_KEYWORDS") or []

def set_topic_keywords(uid, keywords):
    dB.set_var(uid, "AUTOREPLY_TOPIC_KEYWORDS", keywords)

def get_topic_responses(uid):
    return dB.get_var(uid, "AUTOREPLY_TOPIC_RESPONSES") or []

def set_topic_responses(uid, responses):
    dB.set_var(uid, "AUTOREPLY_TOPIC_RESPONSES", responses)

# ================================ AUTOREPLY NON-TOPIC ================================

@zb.ubot("autoreply")
async def _(c, m, _):
    em = Emojik(c)
    em.initialize()
    args = m.text.split(None, 1)
    if len(args) < 2:
        return await m.reply(f"{em.gagal} <i>Gunakan .autoreply on/off/status</i>")
    cmd = args[1].strip().lower()
    if cmd == "on":
        set_autoreply_status(c.me.id, True)
        return await m.reply(f"{em.sukses} <i>AutoReply diaktifkan.</i>")
    elif cmd == "off":
        set_autoreply_status(c.me.id, False)
        return await m.reply(f"{em.gagal} <i>AutoReply dimatikan.</i>")
    elif cmd == "status":
        status = get_autoreply_status(c.me.id)
        log_group = get_log_group(c.me.id)
        log_group_str = f"<code>{log_group}</code>" if log_group else "<i>Belum diatur</i>"
        return await m.reply(
            f"{em.sukses if status else em.gagal} <i>Status AutoReply: {'ON' if status else 'OFF'}</i>\n"
            f"<b>Group Log:</b> {log_group_str}"
        )
    else:
        return await m.reply(f"{em.gagal} <i>Gunakan .autoreply on/off/status</i>")

@zb.ubot("autoreplylog")
async def _(c, m, _):
    em = Emojik(c)
    em.initialize()
    log_group = get_log_group(c.me.id)
    if log_group:
        try:
            chat = await c.get_chat(log_group)
            group_title = chat.title or "-"
            username = f"@{chat.username}" if chat.username else f"<code>{log_group}</code>"
            group_link = f"https://t.me/{chat.username}" if chat.username else f"https://t.me/c/{str(log_group)[4:] if str(log_group).startswith('-100') else log_group}/1"
        except Exception:
            group_title = "-"
            username = f"<code>{log_group}</code>"
            group_link = f"https://t.me/c/{str(log_group)[4:] if str(log_group).startswith('-100') else log_group}/1"
        return await m.reply(
            f"{em.sukses} <b>Group log AutoReply sudah dibuat sebelumnya!</b>\n"
            f"• Nama: <code>{group_title}</code>\n"
            f"• Username/ID: {username}\n"
            f"• Link: <a href=\"{group_link}\">{group_link}</a>\n\n"
            "Hanya bisa membuat 1 group log per user.\nJadikan Ubot Admin "
        )
    try:
        title = f"AutoReply Log {c.me.first_name or ''}".strip()
        group = await c.create_supergroup(title)
        link: ChatInviteLink = await c.create_chat_invite_link(
            group.id, name="AutoReply Log Link", creates_join_request=False
        )
        try:
            await c.join_chat(link.invite_link)
            join_msg = "dan UBot telah join!"
        except Exception as e:
            if "USER_ALREADY_PARTICIPANT" in str(e):
                join_msg = "dan UBot sudah join!"
            else:
                return await m.reply(f"{em.gagal} <i>UBot gagal join ke grup log: {e}</i>")
        set_log_group(c.me.id, group.id)
        await m.reply(
            f"{em.sukses} <b>Group log AutoReply berhasil dibuat {join_msg}</b>\n"
            f"• Nama: <code>{group.title}</code>\n"
            f"• ID: <code>{group.id}</code>\n"
            f"• Link: <a href=\"{link.invite_link}\">Join Group Log</a>\n\n"
            "Notifikasi log autoreply sekarang akan dikirim ke grup ini.\Jadikan ubot Admin"
        )
    except Exception as err:
        await m.reply(f"{em.gagal} <i>Gagal membuat group log: {err}</i>")

@zb.ubot("addautoreply")
async def _(c, m, _):
    em = Emojik(c)
    em.initialize()
    if m.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        return await m.reply(f"{em.gagal} <i>Harus dijalankan di group</i>")
    groups = get_autoreply_groups(c.me.id)
    if m.chat.id not in groups:
        groups.append(m.chat.id)
        set_autoreply_groups(c.me.id, groups)
        await m.reply(f"{em.sukses} <i>Group ditambahkan ke daftar AutoReply.</i>")
    else:
        await m.reply(f"{em.gagal} <i>Group sudah ada dalam daftar.</i>")

@zb.ubot("delautoreply")
async def _(c, m, _):
    em = Emojik(c)
    em.initialize()
    groups = get_autoreply_groups(c.me.id)
    if m.chat.id in groups:
        groups.remove(m.chat.id)
        set_autoreply_groups(c.me.id, groups)
        await m.reply(f"{em.sukses} <i>Group dihapus dari AutoReply.</i>")
    else:
        await m.reply(f"{em.gagal} <i>Group tidak ada dalam daftar.</i>")

@zb.ubot("listautoreply")
async def _(c, m, _):
    em = Emojik(c)
    em.initialize()
    groups = get_autoreply_groups(c.me.id)
    if not groups:
        return await m.reply(f"{em.gagal} <i>Daftar kosong.</i>")
    text = "<b>Daftar Group AutoReply:</b>\n\n"
    for gid in groups:
        try:
            chat = await c.get_chat(gid)
            text += f"<code>{gid}</code> - {chat.title}\n"
        except Exception:
            text += f"<code>{gid}</code>\n"
    await m.reply(text)

@zb.ubot("addreply")
async def _(c, m, _):
    em = Emojik(c)
    em.initialize()
    args = m.text.split(None, 1)
    if len(args) < 2:
        return await m.reply(f"{em.gagal} <i>Format: .addreply [keyword]</i>")
    keyword = args[1].strip()
    if not keyword:
        return await m.reply(f"{em.gagal} <i>Kata kunci tidak boleh kosong</i>")
    keywords = get_keywords(c.me.id)
    if any(x["keyword"].lower() == keyword.lower() for x in keywords):
        return await m.reply(f"{em.gagal} <i>Keyword sudah ada</i>")
    keywords.append({"keyword": keyword})
    set_keywords(c.me.id, keywords)
    await m.reply(f"{em.sukses} <b>Keyword \"{keyword}\" ditambahkan.</b>")

@zb.ubot("addauto")
async def _(c, m, _):
    em = Emojik(c)
    em.initialize()
    args = m.text.split(None, 1)
    if not m.reply_to_message or len(args) < 2:
        return await m.reply(f"{em.gagal} <i>Balas pesan dan gunakan format: .addauto [keyword]</i>")
    keyword = args[1].strip()
    rep = m.reply_to_message
    send = await rep.copy("me")
    responses = get_responses(c.me.id)
    responses = [r for r in responses if r["keyword"].lower() != keyword.lower()]
    media_type = rep.media.value if rep.media else "text"
    responses.append({
        "keyword": keyword,
        "type": media_type,
        "message_id": send.id,
    })
    set_responses(c.me.id, responses)
    await m.reply(f"{em.sukses} <i>Balasan untuk \"{keyword}\" disimpan.</i>")

@zb.ubot("listreply")
async def _(c, m, _):
    em = Emojik(c)
    em.initialize()
    keywords = get_keywords(c.me.id)
    if not keywords:
        return await m.reply(f"{em.gagal} <i>Tidak ada keyword reply.</i>")
    text = "<b>Daftar Keyword AutoReply:</b>\n"
    for idx, item in enumerate(keywords, 1):
        text += f"{idx}. <code>{item['keyword']}</code>\n"
    await m.reply(text)

@zb.ubot("listauto")
async def _(c, m, _):
    em = Emojik(c)
    em.initialize()
    responses = get_responses(c.me.id)
    if not responses:
        return await m.reply(f"{em.gagal} <i>Tidak ada balasan auto.</i>")
    text = "<b>Daftar Balasan AutoReply:</b>\n"
    for idx, item in enumerate(responses, 1):
        text += f"{idx}. <code>{item['keyword']}</code>\n"
    await m.reply(text)

@zb.ubot("delreply")
async def _(c, m, _):
    em = Emojik(c)
    em.initialize()
    args = m.text.split(None, 1)
    if len(args) < 2:
        return await m.reply(f"{em.gagal} <i>Format: .delreply [keyword]</i>")
    keyword = args[1].strip()
    keywords = get_keywords(c.me.id)
    filtered = [x for x in keywords if x["keyword"].lower() != keyword.lower()]
    set_keywords(c.me.id, filtered)
    await m.reply(f"{em.sukses} <i>Keyword \"{keyword}\" dihapus.</i>")

@zb.ubot("delauto")
async def _(c, m, _):
    em = Emojik(c)
    em.initialize()
    args = m.text.split(None, 1)
    if len(args) < 2:
        return await m.reply(f"{em.gagal} <i>Format: .delauto [keyword]</i>")
    keyword = args[1].strip()
    responses = get_responses(c.me.id)
    filtered = [x for x in responses if x["keyword"].lower() != keyword.lower()]
    set_responses(c.me.id, filtered)
    await m.reply(f"{em.sukses} <i>Balasan untuk \"{keyword}\" dihapus.</i>")

# ================================ AUTOREPLY TOPIC (KHUSUS GROUP BERTOPIK) ================================

@zb.ubot("addautoreplytopic")
async def _(c, m, _):
    em = Emojik(c)
    em.initialize()
    if m.chat.type != ChatType.SUPERGROUP:
        return await m.reply(f"{em.gagal} <i>Hanya untuk group bertopik (supergroup).</i>")
    groups = get_topic_groups(c.me.id)
    if m.chat.id not in groups:
        groups.append(m.chat.id)
        set_topic_groups(c.me.id, groups)
        set_topic_status(c.me.id, True)
        await m.reply(f"{em.sukses} <i>AutoReply Topic diaktifkan untuk group ini.</i>")
    else:
        await m.reply(f"{em.gagal} <i>Sudah aktif untuk group ini.</i>")
#@moire_mor
@zb.ubot("addreplytopic")
async def _(c, m, _):
    em = Emojik(c)
    em.initialize()
    if m.chat.type != ChatType.SUPERGROUP:
        return await m.reply(f"{em.gagal} <i>Hanya untuk group bertopik.</i>")
    groups = get_topic_groups(c.me.id)
    if m.chat.id not in groups:
        return await m.reply(f"{em.gagal} <i>Aktifkan dulu dengan .addautoreplytopic</i>")
    args = m.text.split(None, 1)
    if len(args) < 2:
        return await m.reply(f"{em.gagal} <i>Format: .addreplytopic [keyword]</i>")
    keyword = args[1].strip()
    if not keyword:
        return await m.reply(f"{em.gagal} <i>Kata kunci tidak boleh kosong</i>")
    keywords = get_topic_keywords(c.me.id)
    # 1 keyword global topic, berlaku ke semua group bertopik yg aktif
    if any(x["keyword"].lower() == keyword.lower() for x in keywords):
        return await m.reply(f"{em.gagal} <i>Keyword sudah ada untuk AutoReply Topic</i>")
    keywords.append({"keyword": keyword})
    set_topic_keywords(c.me.id, keywords)
    await m.reply(f"{em.sukses} <b>Keyword \"{keyword}\" ditambahkan untuk AutoReply Topic.</b>")

@zb.ubot("addautotopic")
async def _(c, m, _):
    em = Emojik(c)
    em.initialize()
    if m.chat.type != ChatType.SUPERGROUP:
        return await m.reply(f"{em.gagal} <i>Hanya untuk group bertopik.</i>")
    groups = get_topic_groups(c.me.id)
    if m.chat.id not in groups:
        return await m.reply(f"{em.gagal} <i>Aktifkan dulu dengan .addautoreplytopic</i>")
    args = m.text.split(None, 1)
    if not m.reply_to_message or len(args) < 2:
        return await m.reply(f"{em.gagal} <i>Balas pesan & gunakan format: .addautotopic [keyword]</i>")
    keyword = args[1].strip()
    rep = m.reply_to_message
    send = await rep.copy("me")
    responses = get_topic_responses(c.me.id)
    responses = [r for r in responses if r["keyword"].lower() != keyword.lower()]
    media_type = rep.media.value if rep.media else "text"
    responses.append({
        "keyword": keyword,
        "type": media_type,
        "message_id": send.id,
    })
    set_topic_responses(c.me.id, responses)
    await m.reply(f"{em.sukses} <i>Balasan untuk \"{keyword}\" disimpan untuk AutoReply Topic.</i>")

@zb.ubot("delreplytopic")
async def _(c, m, _):
    em = Emojik(c)
    em.initialize()
    args = m.text.split(None, 1)
    if len(args) < 2:
        return await m.reply(f"{em.gagal} <i>Format: .delreplytopic [keyword]</i>")
    keyword = args[1].strip()
    keywords = get_topic_keywords(c.me.id)
    filtered = [x for x in keywords if x["keyword"].lower() != keyword.lower()]
    set_topic_keywords(c.me.id, filtered)
    await m.reply(f"{em.sukses} <i>Keyword \"{keyword}\" dihapus dari AutoReply Topic.</i>")

@zb.ubot("delautotopic")
async def _(c, m, _):
    em = Emojik(c)
    em.initialize()
    args = m.text.split(None, 1)
    if len(args) < 2:
        return await m.reply(f"{em.gagal} <i>Format: .delautotopic [keyword]</i>")
    keyword = args[1].strip()
    responses = get_topic_responses(c.me.id)
    filtered = [x for x in responses if x["keyword"].lower() != keyword.lower()]
    set_topic_responses(c.me.id, filtered)
    await m.reply(f"{em.sukses} <i>Balasan untuk \"{keyword}\" dihapus dari AutoReply Topic.</i>")

@zb.ubot("listautoreplytopic")
async def _(c, m, _):
    em = Emojik(c)
    em.initialize()
    groups = get_topic_groups(c.me.id)
    if not groups:
        return await m.reply(f"{em.gagal} <i>Belum ada group bertopik yang diaktifkan.</i>")
    text = "<b>Daftar Group AutoReply Topic:</b>\n\n"
    for gid in groups:
        try:
            chat = await c.get_chat(gid)
            text += f"<code>{gid}</code> - {chat.title}\n"
        except Exception:
            text += f"<code>{gid}</code>\n"
    await m.reply(text)

@zb.ubot("listreplytopic")
async def _(c, m, _):
    em = Emojik(c)
    em.initialize()
    keywords = get_topic_keywords(c.me.id)
    if not keywords:
        return await m.reply(f"{em.gagal} <i>Tidak ada keyword AutoReply Topic.</i>")
    text = "<b>Daftar Keyword AutoReply Topic:</b>\n"
    for idx, item in enumerate(keywords, 1):
        text += f"{idx}. <code>{item['keyword']}</code>\n"
    await m.reply(text)

@zb.ubot("listautotopic")
async def _(c, m, _):
    em = Emojik(c)
    em.initialize()
    responses = get_topic_responses(c.me.id)
    if not responses:
        return await m.reply(f"{em.gagal} <i>Tidak ada balasan AutoReply Topic.</i>")
    text = "<b>Daftar Balasan AutoReply Topic:</b>\n"
    for idx, item in enumerate(responses, 1):
        text += f"{idx}. <code>{item['keyword']}</code> [{item['type']}]\n"
    await m.reply(text)

# ================================ LISTENER GABUNGAN ================================

@nlx.on_message(
    (filters.text | filters.caption) &
    ~filters.command([
        "autoreply", "addautoreply", "delautoreply", "listautoreply", "addreply", "addauto", "listreply", "listauto", "delreply", "delauto", "autoreplylog",
        "addautoreplytopic", "addreplytopic", "addautotopic", "delreplytopic", "delautotopic", "listautoreplytopic", "listautotopic", "listreplytopic"
    ]),
    group=99
)
async def autoreply_main_listener(client, message: Message):
    # === NON-TOPIC ===
    if message.chat and message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        status = get_autoreply_status(client.me.id)
        groups = get_autoreply_groups(client.me.id)
        if status and message.chat.id in groups:
            responses = get_responses(client.me.id)
            text = message.text or message.caption or ""
            for item in responses:
                if item["keyword"].lower() in text.lower():
                    try:
                        pesan = await client.get_messages("me", item["message_id"])
                        await pesan.copy(message.chat.id, reply_to_message_id=message.id)
                    except Exception:
                        pass
                    try:
                        log_group = get_log_group(client.me.id)
                        if log_group:
                            user = message.from_user
                            user_name = f"{user.first_name} {user.last_name or ''}" if user else "Unknown"
                            group_name = message.chat.title if message.chat.title else str(message.chat.id)
                            notif_text = (
                                f"🔔 <b>AutoReply Detected!</b>\n"
                                f"• <b>Group:</b> {group_name}\n"
                                f"• <b>User:</b> {user_name}\n"
                            )
                            group_id = str(message.chat.id)
                            if group_id.startswith("-100"):
                                group_id_link = group_id[4:]
                            else:
                                group_id_link = group_id
                            message_link = f"https://t.me/c/{group_id_link}/{message.id}"
                            button = ikb([[("lihat group", message_link, "url")]])
                            await bot.send_message(
                                log_group,
                                notif_text,
                                reply_markup=button,
                                disable_web_page_preview=True,
                            )
                    except Exception:
                        pass
                    break

    # === TOPIC ===
    if message.chat and message.chat.type == ChatType.SUPERGROUP:
        topic_status = get_topic_status(client.me.id)
        topic_groups = get_topic_groups(client.me.id)
        if topic_status and message.chat.id in topic_groups:
            keywords = get_topic_keywords(client.me.id)
            responses = get_topic_responses(client.me.id)
            text = message.text or message.caption or ""
            matched = None
            for item in keywords:
                if item["keyword"].lower() in text.lower():
                    matched = item["keyword"]
                    break
            if matched:
                for resp in responses:
                    if resp["keyword"].lower() == matched.lower():
                        try:
                            pesan = await client.get_messages("me", resp["message_id"])
                            await pesan.copy(message.chat.id, reply_to_message_id=message.id)
                        except Exception:
                            pass
                        try:
                            log_group = get_log_group(client.me.id)
                            if log_group:
                                user = message.from_user
                                user_name = f"{user.first_name} {user.last_name or ''}" if user else "Unknown"
                                group_name = message.chat.title if message.chat.title else str(message.chat.id)
                                notif_text = (
                                    f"🔔 <b>AutoReply Topic Detected!</b>\n"
                                    f"• <b>Group:</b> {group_name}\n"
                                    f"• <b>User:</b> {user_name}\n"
                                    f"• <b>Keyword:</b> {matched}\n"
                                )
                                group_id = str(message.chat.id)
                                if group_id.startswith("-100"):
                                    group_id_link = group_id[4:]
                                else:
                                    group_id_link = group_id
                                message_link = f"https://t.me/c/{group_id_link}/{message.id}"
                                button = ikb([[("lihat group", message_link, "url")]])
                                await bot.send_message(
                                    log_group,
                                    notif_text,
                                    reply_markup=button,
                                    disable_web_page_preview=True,
                                )
                        except Exception:
                            pass
                        break
