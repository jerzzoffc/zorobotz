import aiohttp
import os
import filetype
import json
from pyrogram import Client, filters
from pyrogram.types import Message
from config import botcax_api
from Userbot.helper.tools import Emojik, h_s, zb
from Userbot import nlx

# Tambahkan import PIL
from PIL import Image

__MODULES__ = "Remini"

def help_string(org):
    return h_s(org, "help_remini")

async def upload_media(m: Message):
    media = await m.reply_to_message.download()
    try:
        with open(media, "rb") as file:
            file_data = file.read()
            ext = filetype.guess_extension(file_data) or "jpg"
            
        form_data = aiohttp.FormData()
        form_data.add_field("fileToUpload", open(media, "rb"), filename=f"file.{ext}")
        form_data.add_field("reqtype", "fileupload")
        
        async with aiohttp.ClientSession() as session:
            async with session.post("https://catbox.moe/user/api.php", data=form_data) as res:
                if res.status == 200:
                    url = await res.text()
                    return url.strip()
                else:
                    return None
    finally:
        os.remove(media)

@zb.ubot("hd|remini")
async def remove_watermark(client, message: Message, *args):
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.reply_text("Reply ke foto yang ingin di HD.")
        return
    
    await message.reply_text(f"<emoji id=5429411030960711866>💬</emoji> Proses HD...")

    url = await upload_media(message)
    if not url:
        await message.reply_text(f"<emoji id=5260342697075416641>❌</emoji> Gagal mengunggah gambar.")
        return

    api_url = f"https://api.botcahx.eu.org/api/tools/remini-v4?url={url}&resolusi=16&apikey={botcax_api}"
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as res:
            if res.status == 200:
                api_response = await res.text()
                try:
                    data = json.loads(api_response)
                    image_url = data.get("url")
                    if not image_url:
                        await message.reply_text(f"<emoji id=5260342697075416641>❌</emoji> Gagal mendapatkan URL gambar dari API.")
                        return
                except Exception as e:
                    await message.reply_text(f"<emoji id=5260342697075416641>❌</emoji> Error parsing API response: {e}")
                    return

                # Download the image from the URL
                async with session.get(image_url) as img_res:
                    if img_res.status == 200:
                        image_data = await img_res.read()
                        kind = filetype.guess(image_data)
                        if not kind or not kind.mime.startswith("image"):
                            await message.reply_text(f"<emoji id=5260342697075416641>❌</emoji> Gambar hasil API tidak valid. {image_url}")
                            return

                        image_path = f"no_watermark.{kind.extension}"
                        with open(image_path, "wb") as f:
                            f.write(image_data)

                        # PATCH: Periksa dan perbaiki dimensi gambar sebelum dikirim ke Telegram
                        try:
                            with Image.open(image_path) as img:
                                width, height = img.size
                                # Telegram: min 10x10, maks 1280x1280
                                if width < 10 or height < 10 or width > 1280 or height > 1280:
                                    max_size = 1280
                                    img.thumbnail((max_size, max_size))
                                    img.save(image_path)
                                # Pastikan format JPEG
                                if img.format != "JPEG":
                                    rgb_img = img.convert("RGB")
                                    rgb_img.save(image_path, format="JPEG")
                        except Exception as e:
                            await message.reply_text(f"Error cek/resize gambar: {e}")
                            os.remove(image_path)
                            return

                        await message.reply_photo(image_path, caption="<emoji id=5257974976094412956>🖼</emoji> Image berhasil di HD_kan.")
                        os.remove(image_path)
                    else:
                        await message.reply_text(f"<emoji id=5260342697075416641>❌</emoji> Gagal mengunduh gambar dari link API.")
            else:
                await message.reply_text(f"<emoji id=5260342697075416641>❌</emoji> Terjadi kesalahan saat menghubungi API.")
