import http.client
import json
from datetime import datetime, timedelta
from pyrogram import Client, filters
from Userbot.helper.tools import Emojik, h_s, zb
from bs4 import BeautifulSoup


RAPIDAPI_KEY = "0aef743727mshcb5fc9aa289edeep1d40a4jsn4f3ff7bf7798"
RAPIDAPI_HOST = "gmailnator.p.rapidapi.com"

_sessions_gmailnator = {}

def _conn():
    return http.client.HTTPSConnection(RAPIDAPI_HOST)

def _headers(content_type=True):
    h = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST,
    }
    if content_type:
        h["Content-Type"] = "application/json"
    return h

def _parse_json(res):
    try:
        return json.loads(res)
    except Exception:
        return {}

def _extract_text(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text().strip()

@zb.ubot("generateemail")
async def generate_email(client, message, *args):
    user_id = message.from_user.id
    # Hapus session lama
    if user_id in _sessions_gmailnator:
        del _sessions_gmailnator[user_id]
    conn = _conn()
    payload = json.dumps({"options": [1, 2, 3]})
    conn.request("POST", "/generate-email", payload, _headers())
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    result = _parse_json(data)
    email = result.get("email")
    if not email:
        return await message.reply_text("⚠️ Gagal generate email baru!")
    _sessions_gmailnator[user_id] = {
        "email": email,
        "created_at": datetime.utcnow()
    }
    await message.reply_text(
        f"✅ Temp Gmail Anda:\n📩 Email: `{email}`\n\n"
        f"➡ Gunakan perintah `.inbox` untuk cek inbox.\n"
        f"➡ Gunakan perintah `.generateemail` lagi untuk reset email."
    )

@zb.ubot("inbox")
async def gmailnator_inbox(client, message, *args):
    user_id = message.from_user.id
    session = _sessions_gmailnator.get(user_id)
    if not session or "email" not in session:
        return await message.reply_text("⚠️ Anda belum generate email!\nGunakan `.generateemail` dulu.")
    email = session["email"]
    conn = _conn()
    payload = json.dumps({"email": email, "limit": 10})
    conn.request("POST", "/inbox", payload, _headers())
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    result = _parse_json(data)
    if isinstance(result, list):
        inbox = result
    elif isinstance(result, dict):
        inbox = result.get("messages", [])
    else:
        inbox = []
    if not inbox:
        return await message.reply_text(f"📭 Belum ada pesan masuk di `{email}`.")
    out = []
    for msg in inbox:
        pengirim = msg.get("from", "Tidak diketahui")
        subjek = msg.get("subject", "Tidak diketahui")
        waktu = msg.get("date", "Waktu tidak tersedia")
        isi = msg.get("content", msg.get("snippet", "Tidak ada isi"))
        if isi:
            isi = _extract_text(str(isi))
        mid = msg.get("id", "-")
        out.append(
            f"<blockquote>📬 **Pesan Baru!**\n"
            f"💌 **Dari:** `{pengirim}`\n"
            f"🕒 **Waktu:** `{waktu}`\n"
            f"📚 **Subjek:** {subjek}\n"
            f"🔑 **ID:** `{mid}`\n"
            f"📜 **Isi:** `{isi}`</blockquote>"
        )
    await message.reply_text("\n\n".join(out), disable_web_page_preview=True)

@zb.ubot("delete")
async def gmailnator_delete(client, message, *args):
    if not args:
        return await message.reply_text("🔑 Masukkan ID pesan yang ingin dihapus!\nContoh: `.delete <id>`")
    email_id = args[0]
    conn = _conn()
    conn.request("GET", f"/delete?id={email_id}", headers=_headers(content_type=False))
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    result = _parse_json(data)
    if result.get("status") or "success" in data.lower():
        await message.reply_text("🧹 Pesan berhasil dihapus!")
    else:
        await message.reply_text("⚠️ Gagal menghapus pesan.")

@zb.ubot("updatemyemail")
async def gmailnator_update(client, message, *args):
    conn = _conn()
    conn.request("GET", "/update-my-email", headers=_headers(content_type=False))
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    result = _parse_json(data)
    email = result.get("email")
    if not email:
        await message.reply_text("⚠️ Gagal update email!")
    else:
        await message.reply_text(f"🔄 Email Anda yang baru: `{email}`")

@zb.ubot("bulkemails")
async def gmailnator_bulk(client, message, *args):
    conn = _conn()
    payload = json.dumps({"limit": 20, "options": [1, 2, 3]})
    conn.request("POST", "/bulk-emails", payload, _headers())
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    result = _parse_json(data)
    emails = result.get("emails") or result.get("result")
    if not emails:
        return await message.reply_text("⚠️ Gagal generate bulk email!")
    if isinstance(emails, list):
        text = "\n".join(f"- `{e}`" for e in emails)
    else:
        text = str(emails)
    await message.reply_text(f"Bulk email (max 20):\n{text}")
