import os
import asyncio
from PIL import Image, ImageFilter, ImageEnhance
from pyrogram.errors import RPCError
from Userbot.helper.tools import zb, Emojik, get, h_s

__MODULES__ = "RepostStory"

def help_string(org):
    return h_s(org, "help_repost")

def text_to_image(text, out_path, width=900, height=1600, font_size=46):
    from PIL import ImageDraw, ImageFont
    img = Image.new("RGB", (width, height), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()
    margin = 40
    offset = 100
    for line in text.split('\n'):
        draw.text((margin, offset), line, font=font, fill=(255, 255, 255))
        offset += font_size + 10
    img.save(out_path, "JPEG", quality=94)
    return out_path

def make_blur_story(src_path):
    """Bikin gambar story dengan blur background + thumbnail utama di tengah, dan background lebih gelap."""
    # Ukuran story: 1080x1920
    canvas_size = (1080, 1920)
    with Image.open(src_path) as im:
        # Convert ke RGB (jaga-jaga png/webp)
        im = im.convert('RGB')
        # Resize agar thumbnail utama muat di tengah story
        main_width = 500
        aspect = im.height / im.width
        main_height = int(main_width * aspect)
        thumb = im.resize((main_width, main_height), Image.LANCZOS)

        # Blur background
        blur_bg = im.resize(canvas_size, Image.LANCZOS).filter(ImageFilter.GaussianBlur(25))

        # --- Tambahkan penggelapan background di sini! ---
        enhancer = ImageEnhance.Brightness(blur_bg)
        blur_bg = enhancer.enhance(0.8)  # Nilai <1.0 = lebih gelap. Ubah jika perlu (0.5-0.7)
        # -------------------------------------------------

        # Tempel thumbnail di tengah
        pos_x = (canvas_size[0] - main_width)//2
        pos_y = (canvas_size[1] - main_height)//2
        blur_bg.paste(thumb, (pos_x, pos_y))
        out_path = src_path + ".story.jpg"
        blur_bg.save(out_path, "JPEG", quality=94)
    return out_path

@zb.ubot("repost")
async def repost_story(client, message, _):
    proc_msg = await message.reply("<blockquote>⏳ Memproses repost ke story...</blockquote>")
    await asyncio.sleep(1)
    reply = message.reply_to_message
    temp_file = None
    story_file = None

    if not reply:
        await proc_msg.edit("<blockquote>Balas/reply ke pesan yang ingin direpost ke story!</blockquote>")
        return

    try:
        chat_id = client.me.id

        # === MEDIA: photo, document image, video (gif) ===
        if reply.photo or (
            reply.document and reply.document.mime_type and reply.document.mime_type.startswith("image/")
        ):
            temp_file = await reply.download()
            # Proses blur style Telegram
            story_file = make_blur_story(temp_file)
            caption = reply.caption or reply.text or ""
            entities = reply.caption_entities or reply.entities if (reply.caption_entities or reply.entities) else None
            await client.send_story(
                chat_id=chat_id,
                media=story_file,
                caption=caption,
                caption_entities=entities
            )
        # === VIDEO / GIF ===
        elif reply.video or (reply.document and reply.document.mime_type and reply.document.mime_type.startswith("video/")):
            temp_file = await reply.download()
            # Untuk video, tidak bisa blur background dengan cara di atas
            caption = reply.caption or reply.text or ""
            entities = reply.caption_entities or reply.entities if (reply.caption_entities or reply.entities) else None
            await client.send_story(
                chat_id=chat_id,
                media=temp_file,
                caption=caption,
                caption_entities=entities
            )
        # === TEXT ONLY ===
        elif reply.text or reply.caption:
            story_text = reply.text or reply.caption
            temp_file = "story_text.jpg"
            text_to_image(story_text, temp_file)
            await client.send_story(
                chat_id=chat_id,
                media=temp_file,
                caption=""  # Tidak perlu caption, karena teks sudah di gambar
            )
        else:
            await proc_msg.edit("<blockquote>Tidak bisa repost: media tidak didukung.</blockquote>")
            return

        await proc_msg.edit("<blockquote>✅ Berhasil repost ke story dengan style Telegram!</blockquote>")
    except RPCError as e:
        await proc_msg.edit(f"<blockquote>❌ Gagal repost ke story:<br><code>{e.MESSAGE}</code></blockquote>")
    except Exception as e:
        await proc_msg.edit(f"<blockquote>❌ Gagal repost ke story:<br><code>{e}</code></blockquote>")
    finally:
        # Bersihkan file sementara
        for f in [temp_file, story_file]:
            if f and os.path.exists(f):
                try:
                    os.remove(f)
                except Exception:
                    pass
