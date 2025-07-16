import requests
from pyrogram.enums import ChatAction
from pyrogram import filters
from config import botcax_api
from Userbot.helper.tools import zb, h_s
from Userbot import nlx

__MODULES__ = "KBBI"

def help_string(org):
    return h_s(org, "help_kbbi")

@zb.ubot("kbbi")
async def kbbi_search(client, message, *args):
    try:
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
        if len(message.command) < 2:
            await message.reply_text(
                "❌ Mohon gunakan format\ncontoh : .kbbi pohon"
            )
            return
        kata = message.text.split(' ', 1)[1]
        prs = await message.reply_text("🔍 Mencari arti kata...")
        url = f"https://api.botcahx.eu.org/api/search/kbbi?text={kata}&apikey={botcax_api}"
        response = requests.get(url)
        data = response.json()
        if "result" in data:
            arti = data["result"]
            lema = kata.upper()
            hasil = (
                f"<b>📚 TEMA:</b> <b><code>{lema}</code></b>\n"
                f"<b>🔎 ARTI:</b>\n<blockquote>{arti}</blockquote>"
            )
            await prs.edit(hasil)
        elif "message" in data:
            await prs.edit(f"⚠️ {data['message']}")
        else:
            await prs.edit("❌ Tidak ditemukan hasil.")
    except Exception as e:
        await message.reply_text(f"❌ Terjadi error: {e}")
