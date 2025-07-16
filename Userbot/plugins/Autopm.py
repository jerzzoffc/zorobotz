import asyncio
from pyrogram.enums import ChatType
from pyrogram import filters
from Userbot.helper.database import dB
from Userbot import nlx
from Userbot.helper.tools import (Emojik, capture_err, escape_tag, h_s,
                                  initial_ctext, zb, parse_words, ReplyCheck)
import aiohttp
import httpx
from config import botcax_api

__MODULES__ = "AutoPm"

def help_string(org):
    return h_s(org, "help_autopm")

#@moire_mor
DEFAULT_AI_CAR = (
    "Kamu adalah Lana asisten sensei, murid dari sensei blue archive, jangan gunakan saya, aku, gua gunakan lana untuk memanggil dirimu, ekspresi kan sikap kamu mirip seorang murid dari sensei blue archive yang ada di Shittim Chest yang bernama lana, jangan gunakan GPT 4 panggil dirimu dengan lana, Kamu berbicara dengan konsumen, saat berbicara dengannya gunakan emoji, kamu sangat mengerti dengan program userbot, phyton dan lainnya."
)

# --- Storage Helpers ---
def get_filters(uid):
    return dB.get_var(uid, "PMFILTERS") or []

def set_filters(uid, filters_):
    dB.set_var(uid, "PMFILTERS", filters_)

# --- Save message to "me" helper ---
async def save_message_to_me(c, msg):
    logs = "me"
    send = await msg.copy(logs)
    return {
        "type": get_message_type(msg),
        "message_id": send.id,
    }
  
async def ai_autoreply_ai(messages, apikey):
    url = "https://api.botcahx.eu.org/api/search/openai-custom"
    payload = {
        "message": messages,
        "apikey": apikey
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            # botcahx API: result.response atau result
            result = data.get("result", {})
            if isinstance(result, dict):
                return result.get("response", "")
            return result
    except Exception as e:
        print("AI Reply Error:", e)
        return None

def get_message_type(msg):
    if msg.text: return "text"
    if msg.photo: return "photo"
    if msg.sticker: return "sticker"
    if msg.video: return "video"
    if msg.voice: return "voice"
    if msg.audio: return "audio"
    if msg.document: return "document"
    if msg.contact: return "contact"
    if msg.animation: return "animation"
    if msg.video_note: return "video_note"
    return "unknown"

# --- Welcome message (PMWLCM) commands ---
@zb.ubot("pmwlcm")
async def _(c: nlx, m, _):
    arg = c.get_arg(m).lower()
    if arg not in ["on", "off"]:
        return await m.reply("Gunakan `.pmwlcm on` atau `.pmwlcm off`!")
    dB.set_var(c.me.id, "PMWLCM", arg)
    await m.reply(f"<emoji id=5260416304224936047>✅</emoji> PM Welcome Message di-{'aktifkan' if arg == 'on' else 'nonaktifkan'}.")

@zb.ubot("setpmwlcm")#@moire_mor
async def _(c: nlx, m, _):
    if m.reply_to_message:
        saved = await save_message_to_me(c, m.reply_to_message)
        dB.set_var(c.me.id, "PMWLCM_REPLY", saved["message_id"])
        dB.remove_var(c.me.id, "PMWLCM_TEXT")
        await m.reply(f"<emoji id=5260416304224936047>✅</emoji> Pesan sambutan berhasil disimpan")
    else:
        text = c.get_arg(m)
        if not text:
            return await m.reply(f"<emoji id=5258474669769497337>❗️</emoji> Berikan text atau reply pesan untuk disimpan.")
        dB.set_var(c.me.id, "PMWLCM_TEXT", text)
        dB.remove_var(c.me.id, "PMWLCM_REPLY")
        await m.reply(f"<emoji id=5260416304224936047>✅</emoji> Pesan welcome berhasil disimpan.")

@zb.ubot("resetuser")
async def _(c: nlx, m, _):
    if m.reply_to_message:
        user_id = m.reply_to_message.from_user.id
    else:
        arg = c.get_arg(m)
        if not arg or not arg.isdigit():
            return await m.reply(f"<emoji id=5260416304224936047>✅</emoji> Gunakan: `.resetuser [user_id]` atau reply pesan user yang ingin direset.")
        user_id = int(arg)
    dB.remove_var(c.me.id, f"PMWLCM_LAST_{user_id}")
    await m.reply(f"<emoji id=5260416304224936047>✅</emoji> <code>{user_id}</code> berhasil direset untuk pesan welcome.")

# --- Filter commands ---
@zb.ubot("filter")
async def _(c, m, _):
    arg = c.get_arg(m).lower()
    if arg not in ["on", "off"]:
        return await m.reply("<emoji id=5258474669769497337>❗️</emoji> Gunakan `.filter on` atau `.filter off`!")
    dB.set_var(c.me.id, "PMFILTER", arg)
    await m.reply(f"<emoji id=5260416304224936047>✅</emoji> Filter di-{'aktifkan' if arg == 'on' else 'nonaktifkan'}.")

@zb.ubot("addfilter")
async def _(c, m, _):
    args = m.text.split(None, 1)
    if len(args) < 2:
        return await m.reply(f"<emoji id=5258474669769497337>❗️</emoji> Format: `.addfilter [keyword]` (reply pesan)")
    keyword = args[1].strip()
    filters_ = get_filters(c.me.id)
    filters_ = [f for f in filters_ if f["keyword"].lower() != keyword.lower()]
    if m.reply_to_message:
        saved = await save_message_to_me(c, m.reply_to_message)
        filters_.append({
            "keyword": keyword,
            "type": saved["type"],
            "message_id": saved["message_id"],
        })
        set_filters(c.me.id, filters_)
        await m.reply(f"<emoji id=5260416304224936047>✅</emoji> Filter untuk \"{keyword}\" berhasil disimpan.")
    else:
        text = c.get_arg(m)
        if not text:
            return await m.reply(f"<emoji id=5258474669769497337>❗️</emoji> Berikan keyword dan reply pesan.")
        filters_.append({
            "keyword": keyword,
            "type": "text",
            "text": text,
        })
        set_filters(c.me.id, filters_)
        await m.reply(f"<emoji id=5260416304224936047>✅</emoji> Filter untuk \"{keyword}\" berhasil disimpan.")

@zb.ubot("delfilter")
async def _(c, m, _):
    keyword = c.get_arg(m)
    if not keyword:
        return await m.reply(f"<emoji id=5258474669769497337>❗️</emoji> Format: `.delfilter [keyword]`")
    filters_ = get_filters(c.me.id)
    filtered = [f for f in filters_ if f["keyword"].lower() != keyword.lower()]
    set_filters(c.me.id, filtered)
    await m.reply(f"<emoji id=5260416304224936047>✅</emoji> Filter \"{keyword}\" telah dihapus.")

@zb.ubot("listfilter")
async def _(c, m, _):
    filters_ = get_filters(c.me.id)
    if not filters_:
        return await m.reply(f"<emoji id=5258474669769497337>❗️</emoji> Tidak ada filter yang tersimpan.")
    text = "**Daftar Filter:**\n"
    for idx, f in enumerate(filters_, 1):
        text += f"{idx}. `{f['keyword']}`\n"
    await m.reply(text)

@zb.ubot("delallfilter")
async def _(c, m, _):
    set_filters(c.me.id, [])
    await m.reply(f"<emoji id=5260416304224936047>✅</emoji> Berhasil menghapus semua filter.")

# --- AutoAI ON/OFF Commands ---
@zb.ubot("autoai")
async def _(c, m, _):
    arg = c.get_arg(m).lower()
    if arg not in ["on", "off", "setcar"]:
        return await m.reply(f"<emoji id=5258474669769497337>❗️</emoji> Gunakan `.autoai on`, `.autoai off`, atau `.autoai setcar [karakter AI]`!")
    if arg == "on":
        dB.set_var(c.me.id, "AUTO_AI", "on")
        await m.reply(f"<emoji id=5260416304224936047>✅</emoji> Auto AI di-aktifkan.")
    elif arg == "off":
        dB.set_var(c.me.id, "AUTO_AI", "off")
        await m.reply(f"<emoji id=5260416304224936047>✅</emoji> Auto AI di-nonaktifkan.")
    elif arg == "setcar":
        # Bisa dengan reply pesan atau argumen
        if m.reply_to_message and (m.reply_to_message.text or m.reply_to_message.caption):
            car = m.reply_to_message.text or m.reply_to_message.caption
        elif len(args) >= 3 and args[2].strip():
            car = args[2].strip()
        else:
            return await m.reply("<emoji id=5258474669769497337>❗️</emoji> Masukkan teks karakter AI dengan argumen atau reply pesan, contoh: `.autoai setcar [karakter AI kamu]`")
        dB.set_var(c.me.id, "AUTO_AI_CAR", car)
        await m.reply(f"<emoji id=5260416304224936047>✅</emoji> Karakter AI berhasil diatur.")

# --- Listener ---
@nlx.on_message(filters.private & filters.incoming, group=70)
async def quickreply_handler(c, m):
    if m.from_user.is_bot or m.from_user.id == c.me.id:
        return
    replied = False  # Inisialisasi variabel sebelum digunakan
    # Welcome
    if dB.get_var(c.me.id, "PMWLCM") == "on":
        today = m.date.strftime("%Y-%m-%d")
        last_sent = dB.get_var(c.me.id, f"PMWLCM_LAST_{m.from_user.id}")
        if last_sent != today:
            pm_reply_id = dB.get_var(c.me.id, "PMWLCM_REPLY")
            pm_text = dB.get_var(c.me.id, "PMWLCM_TEXT")
            if pm_reply_id:
                try:
                    welcome_msg = await c.get_messages("me", pm_reply_id)
                    await welcome_msg.copy(m.chat.id)
                except Exception as e:
                    print("DEBUG WELCOME REPLY ERROR:", e)
            elif pm_text:
                await c.send_message(m.chat.id, pm_text)
            dB.set_var(c.me.id, f"PMWLCM_LAST_{m.from_user.id}", today)

    # Filter Messages 
    if dB.get_var(c.me.id, "PMFILTER") == "on":
        filters_ = get_filters(c.me.id)
        msg_txt = (m.text or m.caption or "").lower()
        print("DEBUG FILTERS:", filters_)
        print("DEBUG MSG_TXT:", msg_txt)
        for f in filters_:
            print("CHECKING FILTER:", f.get("keyword", "").lower())
            print("FILTER DATA:", f)
            if f.get("keyword", "").lower() in msg_txt:
                print("FILTER MATCHED:", f)
                if "message_id" in f:
                    try:
                        pesan = await c.get_messages("me", f["message_id"])
                        await pesan.copy(m.chat.id)
                        print("DEBUG: Sent reply from message_id (preserve formatting & media)")
                    except Exception as e:
                        print("DEBUG SEND MSG_ID ERROR:", e)
                elif f.get("type") == "text":
                    # fallback jika filter adalah text biasa (tanpa message_id)
                    reply_text = f.get("text")
                    print("REPLY TEXT:", reply_text)
                    if reply_text:
                        try:
                            await c.send_message(m.chat.id, reply_text)
                            print("DEBUG: Sent text filter reply")
                        except Exception as e:
                            print("DEBUG SEND TEXT ERROR:", e)
                break  # hanya satu filter yang direspon
              
    # Auto Reply by AI (jika tidak match filter dan ada pesan text)
    if (
        not replied and (m.text or m.caption)
        and dB.get_var(c.me.id, "AUTO_AI") == "on"
    ):
        user_message = m.text or m.caption or ""
        if user_message.strip():
            # Ambil persona dari database atau pakai default
            persona = dB.get_var(c.me.id, "AUTO_AI_CAR") or DEFAULT_AI_CAR
            messages = [
                {
                    "role": "system",
                    "content": "kamu adalah Lana asisten moire , Seorang murid dari sensei di Blue archive, yang siap membantu konsumen kapan pun."
                },
                {
                    "role": "assistant",
                    "content": persona
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
            try:
                ai_response = await ai_autoreply_ai(messages, botcax_api)
                if ai_response:
                    await m.reply(ai_response)
            except Exception as e:
                print("AI Reply Error:", e)
