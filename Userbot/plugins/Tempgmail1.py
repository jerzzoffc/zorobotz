import http.client
import json
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message
from Userbot.helper.tools import zb
from Userbot import nlx

__MODULES__ = "TempGmail"

RAPIDAPI_KEY = "0aef743727mshcb5fc9aa289edeep1d40a4jsn4f3ff7bf7798"
RAPIDAPI_HOST = "temp-gmail-temporary-disposable-gmail-account.p.rapidapi.com"
SESSION_TIMEOUT = timedelta(minutes=30)

sessions_gmail = {}

def get_temp_gmail():
    conn = http.client.HTTPSConnection(RAPIDAPI_HOST)
    headers = {
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': RAPIDAPI_HOST
    }
    conn.request("GET", "/email", headers=headers)
    res = conn.getresponse()
    data = res.read()
    try:
        result = json.loads(data.decode("utf-8"))
    except Exception:
        result = {"error": "Gagal decode response"}
    return result

def get_inbox_temp_gmail(email):
    conn = http.client.HTTPSConnection(RAPIDAPI_HOST)
    payload = f"email={email}"
    headers = {
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': RAPIDAPI_HOST,
        'Content-Type': "application/x-www-form-urlencoded"
    }
    conn.request("POST", "/messages", payload, headers)
    res = conn.getresponse()
    data = res.read()
    try:
        result = json.loads(data.decode("utf-8"))
    except Exception:
        result = {"error": "Gagal decode response"}
    return result

@zb.ubot("getmail")
async def getmail_cmd(client, message: Message, *args):
    user_id = message.from_user.id

    # Hapus sesi expired
    expired_sessions = [
        uid for uid, data in sessions_gmail.items()
        if datetime.utcnow() - data["created_at"] > SESSION_TIMEOUT
    ]
    for uid in expired_sessions:
        del sessions_gmail[uid]

    if user_id in sessions_gmail:
        email = sessions_gmail[user_id]["email"]
        return await message.reply_text(
            f"✅ Gmail Sementara Anda:\n📩 Email: `{email}`\n"
            f"➡ Gunakan perintah `.getinbox <alamat email>` untuk melihat inbox.\n"
            f"➡ Gunakan perintah `.getmail` lagi untuk generate email baru."
        )

    data = get_temp_gmail()
    email = data.get("email")
    if not email:
        err = data.get("error", "Gagal mendapatkan email.")
        return await message.reply_text(f"⚠️ {err}")

    sessions_gmail[user_id] = {
        "email": email,
        "created_at": datetime.utcnow()
    }

    await message.reply_text(
        f"✅ Gmail Sementara Anda:\n📩 Email: `{email}`\n"
        f"➡ Gunakan perintah `.getinbox <alamat email>` untuk melihat inbox.\n"
        f"➡ Gunakan perintah `.getmail` lagi untuk generate email baru."
    )

@zb.ubot("getinbox")
async def getinbox_cmd(client, message: Message, *args):
    user_id = message.from_user.id

    # Jika user tidak memberi argumen email, cek apakah ada email aktif di sesi
    if not args or not args[0]:
        email = None
        if user_id in sessions_gmail:
            email = sessions_gmail[user_id]["email"]
        if not email:
            return await message.reply_text(
                "❌ Masukkan alamat email atau buat temp mail dulu.\n"
                "Contoh: `.getinbox alamat@email.com`\n"
                "Atau jalankan `.getmail` untuk membuat temp mail."
            )
    else:
        email = args[0]

    data = get_inbox_temp_gmail(email)

    # PATCH: Handle if data is a list or dict
    if isinstance(data, list):
        inbox = data
    elif isinstance(data, dict) and "messages" in data:
        inbox = data["messages"]
    else:
        return await message.reply_text("⚠️ Tidak bisa mengambil inbox, format data tidak dikenali!")

    if not inbox:
        return await message.reply_text(f"📭 Belum ada pesan masuk di `{email}`.")

    pesan_list = []
    for msg in inbox:
        pengirim = msg.get("sender_name", msg.get("sender", "Tidak diketahui"))
        pengirim_email = msg.get("sender_email", "")
        subjek = msg.get("subject", "Tidak diketahui")
        waktu = msg.get("date", "Waktu tidak tersedia")
        isi_pesan = msg.get("content", msg.get("body", "Tidak ada isi"))

        # Optional: strip HTML tags for better readability
        try:
            from bs4 import BeautifulSoup
            isi_pesan = BeautifulSoup(isi_pesan, "html.parser").get_text().strip()
        except Exception:
            pass

        pesan_list.append(
            f"📬 **Pesan Baru!**\n"
            f"💌 **Dari:** `{pengirim}` <{pengirim_email}>\n"
            f"🕒 **Waktu:** `{waktu}`\n"
            f"📚 **Subjek:** {subjek}\n"
            f"📜 **Isi:** `{isi_pesan}`"
        )

    hasil = "\n\n".join(pesan_list)
    await message.reply_text(hasil, disable_web_page_preview=True)
    
@zb.ubot("getallemail")
async def getallemail_cmd(client, message: Message, *args):
    if not sessions_gmail:
        return await message.reply_text("❌ Belum ada email sementara yang dibuat di sesi ini.")
    hasil = []
    for uid, data in sessions_gmail.items():
        waktu = data["created_at"].strftime('%Y-%m-%d %H:%M:%S')
        hasil.append(f"👤 UID: `{uid}`\n📩 Email: `{data['email']}`\n🕒 Dibuat: `{waktu}`")
    await message.reply_text("\n\n".join(hasil))
