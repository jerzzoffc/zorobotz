import base64
import mimetypes
import os
import random
import io
import re
from aiohttp import ClientSession
from Userbot.helper.tools import zb

__MODULES__ = "RemoveBgScraper"

COLOR_ALIASES = {
    "merah": "#FF0000",
    "biru": "#0000FF",
    "hijau": "#00FF00",
    "kuning": "#FFFF00",
    "ungu": "#800080",
    "pink": "#FFC0CB",
    "hitam": "#000000",
    "putih": "#FFFFFF",
    "abu": "#808080",
    "abu-abu": "#808080",
    "oren": "#FFA500",
    "oranye": "#FFA500",
    "coklat": "#A52A2A",
    "cyan": "#00FFFF",
    "magenta": "#FF00FF",
    "transparent": "transparent",
    "transparan": "transparent",
    "default": "transparent"
}
COLOR_LIST = [
    "merah", "biru", "hijau", "kuning", "ungu", "pink", "hitam", "putih", "abu", "oren", "coklat", "cyan", "magenta", "transparent"
]

def resolve_color(user_input):
    color = user_input.lower()
    if color in COLOR_ALIASES:
        return COLOR_ALIASES[color]
    # Validasi HEX format #RRGGBB atau RRGGBB
    if re.match(r"^#?[0-9a-fA-F]{6}$", color):
        if not color.startswith("#"):
            color = "#" + color
        return color.upper()
    return None

@zb.ubot("rmbgx|removebgx")
async def removebg_scraper(client, message, args):
    """
    Remove background dengan pilihan warna background custom.
    Balas ke gambar lalu gunakan perintah di bawah ini.

    .rmbgx help
        → Menampilkan daftar warna yang didukung serta cara pakai.

    .rmbgx [warna]
        → Menghapus background gambar dengan warna background sesuai pilihan.
        Contoh:
        .rmbgx putih      # background putih
        .rmbgx hitam      # background hitam
        .rmbgx merah      # background merah
        .rmbgx #12abef    # HEX custom
        .rmbgx transparent (default) # transparan
    """
    # Pastikan args selalu list of str
    if isinstance(args, str):
        arg_list = args.strip().split()
    elif isinstance(args, (list, tuple)):
        arg_list = list(args)
    else:
        arg_list = []

    # Help/manual command
    if arg_list and arg_list[0].lower() == "help":
        color_text = "\n".join([
            f"- {c} ({COLOR_ALIASES[c]})"
            for c in COLOR_LIST
        ])
        help_msg = (
            "<b>Remove Background dengan Pilihan Warna</b>\n\n"
            "<b>Cara pakai:</b>\n"
            "Balas gambar lalu gunakan:\n"
            "<code>.rmbgx [warna]</code>\n\n"
            "<b>Contoh:</b>\n"
            "<code>.rmbgx putih</code> (background putih)\n"
            "<code>.rmbgx hitam</code> (background hitam)\n"
            "<code>.rmbgx merah</code> (background merah)\n"
            "<code>.rmbgx #12abef</code> (custom HEX)\n"
            "<code>.rmbgx transparent</code> (tanpa background)\n\n"
            "<b>Warna yang didukung (nama/alias atau hex):</b>\n"
            f"{color_text}\n"
            "- transparent (tanpa background)\n"
        )
        return await message.reply(help_msg)
    
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.reply("Reply ke image dulu, bray! Ketik <code>.rmbgx help</code> untuk melihat opsi warna.")

    # Unduh foto
    photo_path = await message.reply_to_message.download()
    try:
        # Dapatkan mime dan ekstensi
        mime = mimetypes.guess_type(photo_path)[0] or "image/jpeg"
        ext = os.path.splitext(photo_path)[1][1:] or "jpg"
        rand = random.randint(10000, 99999)
        title = f"Fiony-{rand}.{ext}"

        # Encode ke base64 (datauri)
        with open(photo_path, "rb") as f:
            b64img = base64.b64encode(f.read()).decode()
        datauri = f"data:{mime};base64,{b64img}"

        color_input = arg_list[0] if arg_list else "transparent"
        color_value = resolve_color(color_input)
        if color_value is None:
            return await message.reply(
                f"Warna tidak dikenali: <b>{color_input}</b>\n"
                "Gunakan <code>.rmbgx help</code> untuk melihat daftar warna yang tersedia!"
            )

        # Penentuan payload API SESUAI website aslinya!
        if color_value == "transparent":
            backgroundMode = "transparent"
            data = {
                "encodedImage": datauri,
                "title": title,
                "mimeType": mime,
                "backgroundMode": backgroundMode
            }
        else:
            backgroundMode = "color"
            data = {
                "encodedImage": datauri,
                "title": title,
                "mimeType": mime,
                "backgroundMode": backgroundMode,
                "backgroundColor": color_value
            }

        headers = {
            "accept": "*/*",
            "content-type": "application/json; charset=utf-8",
            "referer": "https://background-remover.com/upload"
        }

        async with ClientSession() as session:
            async with session.post("https://background-remover.com/removeImageBackground", json=data, headers=headers) as resp:
                res = await resp.json()
                out_b64 = res.get("encodedImageWithoutBackground", "")
                if not out_b64 or "," not in out_b64:
                    raise Exception("Gagal dapet hasil BG remover bro!")
                out_b64_clean = out_b64.split(",")[1]
                img_bytes = base64.b64decode(out_b64_clean)

        img_io = io.BytesIO(img_bytes)
        img_io.name = title  # beri nama agar dikenali sebagai file gambar

        user_color_info = color_input if color_value != "transparent" else "tanpa background"
        await message.reply_photo(img_io, caption=f"Selesai remove background ({user_color_info})!\n\n> <b>Ubot Pro-X</b>")
    except Exception as e:
        detail = str(e)
        await message.reply(f"error: {detail}")
    finally:
        try:
            os.remove(photo_path)
        except Exception:
            pass
