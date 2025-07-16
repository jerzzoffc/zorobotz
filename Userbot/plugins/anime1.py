import random
import requests
from pyrogram.enums import *
from pyrogram import *
from pyrogram.types import *
from io import BytesIO
from config import botcax_api
from Userbot.helper.tools import Emojik, h_s, zb
from Userbot import nlx

__MODULES__ = "Anime1"

def help_string(org):
    return h_s(org, "help_anime1")

URLS = {
    "keneki": f"https://api.botcahx.eu.org/api/anime/keneki?apikey={botcax_api}",
    "megumin": f"https://api.botcahx.eu.org/api/anime/megumin?apikey={botcax_api}",
    "yotsuba": f"https://api.botcahx.eu.org/api/anime/yotsuba?apikey={botcax_api}",
    "shinomiya": f"https://api.botcahx.eu.org/api/anime/shinomiya?apikey={botcax_api}",
    "yumeko": f"https://api.botcahx.eu.org/api/anime/yumeko?apikey={botcax_api}",
    "tsunade": f"https://api.botcahx.eu.org/api/anime/tsunade?apikey={botcax_api}",
    "kagura": f"https://api.botcahx.eu.org/api/anime/kagura?apikey={botcax_api}",
    "madara": f"https://api.botcahx.eu.org/api/anime/madara?apikey={botcax_api}",
    "itachi": f"https://api.botcahx.eu.org/api/anime/itachi?apikey={botcax_api}",
    "akira": f"https://api.botcahx.eu.org/api/anime/akira?apikey={botcax_api}",
    "toukachan": f"https://api.botcahx.eu.org/api/anime/toukachan?apikey={botcax_api}",
    "cicho": f"https://api.botcahx.eu.org/api/anime/chiho?apikey={botcax_api}",
    "sasuke": f"https://api.botcahx.eu.org/api/anime/sasuke?apikey={botcax_api}"
}

@zb.ubot("anime")
async def _(client, message, *args):
    # Extract query from message
    query = message.text.split()[1] if len(message.text.split()) > 1 else None
    
    if query not in URLS:
        valid_queries = ", ".join(URLS.keys())
        await message.reply(f"Query tidak valid. Gunakan salah satu dari: {valid_queries}.")
        return

    processing_msg = await message.reply("Processing....")
    
    try:
        await client.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)
        response = requests.get(URLS[query])
        response.raise_for_status()
        
        photo = BytesIO(response.content)
        photo.name = 'image.jpg'
        
        await client.send_photo(message.chat.id, photo)
        await processing_msg.delete()
    except requests.exceptions.RequestException as e:
        await processing_msg.edit_text(f"Gagal mengambil gambar anime Error: {e}")
