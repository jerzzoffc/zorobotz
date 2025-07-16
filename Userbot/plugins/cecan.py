import random
import requests
from pyrogram.enums import *
from pyrogram import *
from pyrogram.types import *
from io import BytesIO
from Userbot.helper.tools import Emojik, h_s, zb
from Userbot import nlx
from config import botcax_api

__MODULES__ = "Cecan"

def help_string(org):
    return h_s(org, "help_cecan")

URLS = {
    "indonesia": f"https://api.botcahx.eu.org/api/cecan/indonesia?apikey={botcax_api}",
    "china": f"https://api.botcahx.eu.org/api/cecan/china?apikey={botcax_api}",
    "thailand": f"https://api.botcahx.eu.org/api/cecan/thailand?apikey={botcax_api}",
    "vietnam": f"https://api.botcahx.eu.org/api/cecan/vietnam?apikey={botcax_api}",
    "hijaber": f"https://api.botcahx.eu.org/api/cecan/hijaber?apikey={botcax_api}",
    "rose": f"https://api.botcahx.eu.org/api/cecan/rose?apikey={botcax_api}",
    "ryujin": f"https://api.botcahx.eu.org/api/cecan/ryujin?apikey={botcax_api}",
    "jiso": f"https://api.botcahx.eu.org/api/cecan/jiso?apikey={botcax_api}",
    "jeni": f"https://api.botcahx.eu.org/api/cecan/jeni?apikey={botcax_api}",
    "justinaxie": f"https://api.botcahx.eu.org/api/cecan/justinaxie?apikey={botcax_api}",
    "malaysia": f"https://api.botcahx.eu.org/api/cecan/malaysia?apikey={botcax_api}",
    "japan": f"https://api.botcahx.eu.org/api/cecan/japan?apikey={botcax_api}",
    "korea": f"https://api.botcahx.eu.org/api/cecan/korea?apikey={botcax_api}"
}

@zb.ubot("cecan")
async def _(client, message, *args):
    # Extract query from message
    query = message.text.split()[1] if len(message.text.split()) > 1 else None
    
    if query not in URLS:
        valid_queries = ", ".join(URLS.keys())
        await message.reply(f"Query tidak valid. Gunakan salah satu dari: {valid_queries}.")
        return

    processing_msg = await message.reply("Processing.....")
    
    try:
        await client.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)
        response = requests.get(URLS[query])
        response.raise_for_status()
        
        photo = BytesIO(response.content)
        photo.name = 'image.jpg'
        
        await client.send_photo(message.chat.id, photo)
        await processing_msg.delete()
    except requests.exceptions.RequestException as e:
        await processing_msg.edit_text(f"Gagal mengambil gambar cecan Error: {e}")
