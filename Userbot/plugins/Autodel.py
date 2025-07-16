import asyncio
from Userbot.helper.tools import Emojik, zb, h_s
from Userbot import nlx
from Userbot.helper.database import dB
from pyrogram.enums import ChatType
from pyrogram.errors import MessageDeleteForbidden
from pyrogram.types import Message
from pyrogram import filters

__MODULES__ = "AutoDel"

def help_string(org):
    return h_s(org, "help_autodel")

#@moire_mor
def emoji(alias):
    emojis = {
        "GAGAL": "<emoji id=5260342697075416641>❌</emoji>",
        "AKTIF": "<emoji id=5260416304224936047>✅</emoji>",
        "OFFF": "<emoji id=5260342697075416641>❌</emoji>",
        "INFO" : "<emoji id=5258503720928288433>ℹ️</emoji>",
        "WARN" : "<emoji id=5258474669769497337>❗️</emoji>",
        "USER" : "<emoji id=5316727448644103237>👤</emoji>",
    }
    return emojis.get(alias, "•")

ggl = emoji("GAGAL")
aktf   = emoji("AKTIF")
offf  = emoji("OFFF")
inf   = emoji("INFO")
wrn   = emoji("WARN")
usn   = emoji("USER")

PROTECT_GROUPS_KEY = "PROTECT_GROUPS"
BLACKLIST_WORDS_KEY = "BLACKLIST_WORDS"
EXEMPT_USERS_KEY = "EXEMPT_USERS"

def get_exempt_ids(c, group_id):
    exempt = dB.get_var(c.me.id, EXEMPT_USERS_KEY, "PROTECT") or {}
    return set(map(int, exempt.get(str(group_id), [])))

def add_exempt(c, group_id, user_id):
    exempt = dB.get_var(c.me.id, EXEMPT_USERS_KEY, "PROTECT") or {}
    lst = set(map(int, exempt.get(str(group_id), [])))
    lst.add(int(user_id))
    exempt[str(group_id)] = list(lst)
    dB.set_var(c.me.id, EXEMPT_USERS_KEY, exempt, "PROTECT")

def remove_exempt(c, group_id, user_id):
    exempt = dB.get_var(c.me.id, EXEMPT_USERS_KEY, "PROTECT") or {}
    lst = set(map(int, exempt.get(str(group_id), [])))
    lst.discard(int(user_id))
    exempt[str(group_id)] = list(lst)
    dB.set_var(c.me.id, EXEMPT_USERS_KEY, exempt, "PROTECT")

@zb.ubot("autodel")
async def cmd_protect(c: nlx, m, _):
    em = Emojik(c)
    em.initialize()
    if not m.chat or m.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return await m.reply(f"{ggl} Perintah ini hanya bisa di grup!", quote=True)
    args = c.get_arg(m)
    if args not in ["on", "off"]:
        return await m.reply(f"{ggl} Gunakan: .protect on/off", quote=True)
    group_id = m.chat.id
    group_name = m.chat.title

    protect_groups = dB.get_var(c.me.id, PROTECT_GROUPS_KEY, "PROTECT") or {}
    if not isinstance(protect_groups, dict):
        protect_groups = {}

    protect_groups[str(group_id)] = {
        "name": group_name,
        "status": args
    }
    dB.set_var(c.me.id, PROTECT_GROUPS_KEY, protect_groups, "PROTECT")
    status_emoji = aktf if args == "on" else offf
    await m.reply(f"<i>{status_emoji} Proteksi di <b>{group_name}</b>\ntelah <b>{args.upper()}</b></i>", quote=True)

@zb.ubot("addautodel")
async def cmd_addprotect(c: nlx, m, _):
    em = Emojik(c)
    em.initialize()
    if not m.chat or m.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return await m.reply(f"<i>{ggl} Perintah ini hanya bisa di grup!</i>", quote=True)
    group_id = m.chat.id
    group_name = m.chat.title

    protect_groups = dB.get_var(c.me.id, PROTECT_GROUPS_KEY, "PROTECT") or {}
    if not isinstance(protect_groups, dict):
        protect_groups = {}

    if str(group_id) in protect_groups:
        return await m.reply(f"<i>{ggl} Grup ini sudah ada di daftar Autodel.</i>", quote=True)

    protect_groups[str(group_id)] = {
        "name": group_name,
        "status": "off"
    }
    dB.set_var(c.me.id, PROTECT_GROUPS_KEY, protect_groups, "PROTECT")
    await m.reply(
        f"<i>{aktf} Grup <b>{group_name}</b> berhasil ditambahkan ke daftar Autodel!</i>\n"
        f"<i>{inf} <b>ID:</b> <code>{group_id}</code></i>",
        quote=True
    )

@zb.ubot("listautodel")
async def cmd_listprotect(c: nlx, m, _):
    em = Emojik(c)
    em.initialize()
    protect_groups = dB.get_var(c.me.id, PROTECT_GROUPS_KEY, "PROTECT") or {}
    if not protect_groups:
        return await m.reply(f"<i>{wrn} Tidak ada group yang diautodel.</i>", quote=True)
    lines = [f"<i>{inf} <b>{v['name']}</b> <code>{gid}</code> {aktf if v['status']=='on' else offf} </i>"
             for gid, v in protect_groups.items()]
    text = f"{inf} <b>Daftar Group yang diautodel:</b>\n\n" + "\n".join(lines)
    await m.reply(text, quote=True)

@zb.ubot("statusautodel")
async def cmd_statusprotect(c: nlx, m, _):
    em = Emojik(c)
    em.initialize()
    protect_groups = dB.get_var(c.me.id, PROTECT_GROUPS_KEY, "PROTECT") or {}
    if not protect_groups:
        return await m.reply(f"<i>{wrn} Belum ada group dalam autodel.</i>", quote=True)
    text = f"{inf} <b>Status Autodel Group:</b>\n"
    for gid, v in protect_groups.items():
        icon = aktf if v["status"] == "on" else offf
        text += f"\n{inf} <b>{v['name']}</b>\nID: <code>{gid}</code>\nStatus: <b>{v['status'].upper()}</b>"
    await m.reply(text, quote=True)

@zb.ubot("statusgroup")
async def cmd_statusgroup(c: nlx, m, _):
    em = Emojik(c)
    em.initialize()
    if not m.chat or m.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return await m.reply(f"<i>{ggl} Perintah ini hanya bisa di grup!</i>", quote=True)
    group_id = m.chat.id
    group_name = m.chat.title

    protect_groups = dB.get_var(c.me.id, PROTECT_GROUPS_KEY, "PROTECT") or {}
    prot_stat = protect_groups.get(str(group_id), {}).get("status", "off")
    stat_emoji = aktf if prot_stat == "on" else offf

    blacklist_words = dB.get_var(c.me.id, BLACKLIST_WORDS_KEY, "PROTECT") or {}
    words = blacklist_words.get(str(group_id), [])
    await m.reply(
        f"{wrn} <b>Status Grup <i>{group_name}</i>:</b>\n"
        f"ID: <code>{group_id}</code>\n"
        f"Autodel: <b>{prot_stat.upper()}</b>\n"
        f"Blacklist hit: <b>{len(words)}</b>",
        quote=True
    )

@zb.ubot("hit")
async def cmd_word(c: nlx, m, _):
    em = Emojik(c)
    em.initialize()
    if not m.chat or m.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return await m.reply(f"<i>{ggl} Perintah ini hanya bisa di grup!</i>", quote=True)
    group_id = m.chat.id
    word = c.get_arg(m)
    if not word:
        return await m.reply(f"{ggl} Gunakan: .hit [text/replytext]", quote=True)
    blacklist_words = dB.get_var(c.me.id, BLACKLIST_WORDS_KEY, "PROTECT") or {}
    words = blacklist_words.get(str(group_id), [])
    if word.lower() in [w.lower() for w in words]:
        return await m.reply(f"<i>{wrn} Kata sudah ada di blacklist.</i>", quote=True)
    words.append(word)
    blacklist_words[str(group_id)] = words
    dB.set_var(c.me.id, BLACKLIST_WORDS_KEY, blacklist_words, "PROTECT")
    await m.reply(f"<i>{aktf} Kata <b>{word}</b> berhasil ditambahkan ke blacklist!</i>", quote=True)

@zb.ubot("hitlist")
async def cmd_wordlist(c: nlx, m, _):
    em = Emojik(c)
    em.initialize()
    if not m.chat or m.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return await m.reply(f"<i>{ggl} Perintah ini hanya bisa di grup!</i>", quote=True)
    group_id = m.chat.id
    blacklist_words = dB.get_var(c.me.id, BLACKLIST_WORDS_KEY, "PROTECT") or {}
    words = blacklist_words.get(str(group_id), [])
    if not words:
        return await m.reply(f"<i>{wrn} Tidak ada blacklist hit di grup ini.</i>", quote=True)
    lines = [f"• {w}" for w in words]
    text = f"{inf} <b>Blacklist Hit di grup ini:</b>\n" + "\n".join(lines)
    await m.reply(text, quote=True)

@zb.ubot("delhit")
async def cmd_delword(c: nlx, m, _):
    em = Emojik(c)
    em.initialize()
    if not m.chat or m.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return await m.reply(f"{ggl} Perintah ini hanya bisa di grup!", quote=True)
    group_id = m.chat.id
    word = c.get_arg(m)
    if not word:
        return await m.reply(f"<i>{ggl} Gunakan: .delhit [text]</i>", quote=True)
    blacklist_words = dB.get_var(c.me.id, BLACKLIST_WORDS_KEY, "PROTECT") or {}
    words = blacklist_words.get(str(group_id), [])
    if word not in words:
        return await m.reply(f"<i>{ggl} Kata tidak ditemukan di blacklist.</i>", quote=True)
    words = [w for w in words if w.lower() != word.lower()]
    blacklist_words[str(group_id)] = words
    dB.set_var(c.me.id, BLACKLIST_WORDS_KEY, blacklist_words, "PROTECT")
    await m.reply(f"<i>{inf} Kata <b>{word}</b> dihapus dari blacklist!</i>", quote=True)

@zb.ubot("addskip")
async def cmd_addexempt(c: nlx, m, _):
    em = Emojik(c)
    em.initialize()
    if not m.chat or m.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return await m.reply(f"<i>{ggl} Perintah ini hanya di grup!</i>", quote=True)
    target_id = None
    if m.reply_to_message:
        target_id = m.reply_to_message.from_user.id
    else:
        arg = c.get_arg(m)
        if arg and arg.isdigit():
            target_id = int(arg)
    if not target_id:
        return await m.reply(f"<i>{ggl} Balas pesan user atau masukkan user_id.</i>", quote=True)
    add_exempt(c, m.chat.id, target_id)
    await m.reply(f"<i>{usn} User <code>{target_id}</code> ditambahkan ke pengecualian Autodel!</i>", quote=True)

@zb.ubot("delskip")
async def cmd_delexempt(c: nlx, m, _):
    em = Emojik(c)
    em.initialize()
    if not m.chat or m.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return await m.reply(f"<i>{ggl} Perintah ini hanya di grup!</i>", quote=True)
    target_id = None
    if m.reply_to_message:
        target_id = m.reply_to_message.from_user.id
    else:
        arg = c.get_arg(m)
        if arg and arg.isdigit():
            target_id = int(arg)
    if not target_id:
        return await m.reply(f"<i>{ggl} Balas pesan user atau masukkan user_id.</i>", quote=True)
    remove_exempt(c, m.chat.id, target_id)
    await m.reply(f"<i>{usn} User <code>{target_id}</code> dihapus dari pengecualian Autodel!</i>", quote=True)

@zb.ubot("listskip")
async def cmd_listexempt(c: nlx, m, _):
    em = Emojik(c)
    em.initialize()
    if not m.chat or m.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return await m.reply(f"<i>{ggl} Perintah ini hanya di grup!</i>", quote=True)
    group_id = m.chat.id
    exempt_ids = get_exempt_ids(c, group_id)
    if not exempt_ids:
        return await m.reply(f"<i>{wrn} Tidak ada user yang dikecualikan di grup ini.</i>", quote=True)
    lines = []
    for uid in exempt_ids:
        lines.append(f"{inf} <code>{uid}</code>")
    text = f"{usn} <b>User dikecualikan dari Autodel:</b>\n" + "\n".join(lines)
    await m.reply(text, quote=True)


@nlx.on_message(
    (filters.text | filters.caption) &
    ~filters.command([
        "autodel", "addautodel", "listautodel", "statusautodel",
        "statusgroup", "hit", "hitlist", "delhit", "addskip", "delskip", "listskip"
    ]),
    group=100  # PATCH: Pastikan handler jalan terakhir agar tidak blokir handler lain
)
async def auto_delete_blacklist_word(client, message: Message):
    if not message.chat or message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return
    group_id = message.chat.id

    protect_groups = dB.get_var(client.me.id, PROTECT_GROUPS_KEY, "PROTECT") or {}
    group_prot = protect_groups.get(str(group_id), {})
    if group_prot.get("status") != "on":
        return

    blacklist_words = dB.get_var(client.me.id, BLACKLIST_WORDS_KEY, "PROTECT") or {}
    words = set(w.lower() for w in blacklist_words.get(str(group_id), []))
    if not words:
        return

    user_id = message.from_user.id if message.from_user else None
    if not user_id:
        return

    # Admin/owner/superuser
    member = await client.get_chat_member(group_id, user_id)
    if member.status in ("administrator", "creator"):
        return
    from config import owner_id, DEVS
    if user_id == owner_id or user_id in DEVS:
        return
    exempt_ids = get_exempt_ids(client, group_id)
    if user_id in exempt_ids:
        return

    text = message.text or message.caption or ""
    for w in words:
        if w in text.lower():
            try:
                await message.delete()
                notif = await client.send_message(
                    group_id,
                    f"{ggl} Pesan dari <b>{message.from_user.mention if message.from_user else user_id}</b> "
                    f"{wrn} Protect detect blackist hit : <b>{w}</b>",
                    reply_to_message_id=message.id
                )
                await asyncio.sleep(5)
                await notif.delete()
            except MessageDeleteForbidden:
                pass
            break
