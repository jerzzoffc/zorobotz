import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageColor

from ._http import fetch

class QuotlyException(Exception):
    pass

loanjing = [
    "White", "Navy", "DarkBlue", "MediumBlue", "Blue", "DarkGreen", "Green", "Teal",
    "DarkCyan", "DeepSzbBlue", "DarkTurquoise", "MediumSpringGreen", "Lime", "SpringGreen",
    "Aqua", "Cyan", "MidnightBlue", "DodgerBlue", "LightSeaGreen", "ForestGreen", "SeaGreen",
    "DarkSlateGray", "DarkSlateGrey", "LimeGreen", "MediumSeaGreen", "Turquoise", "RoyalBlue",
    "SteelBlue", "DarkSlateBlue", "MediumTurquoise", "Indigo  ", "DarkOliveGreen", "CadetBlue",
    "CornflowerBlue", "RebeccaPurple", "MediumAquaMarine", "DimGray", "DimGrey", "SlateBlue",
    "OliveDrab", "SlateGray", "SlateGrey", "LightSlateGray", "LightSlateGrey", "MediumSlateBlue",
    "LawnGreen", "Chartreuse", "Aquamarine", "Maroon", "Purple", "Olive", "Gray", "Grey",
    "SzbBlue", "LightSzbBlue", "BlueViolet", "DarkRed", "DarkMagenta", "SaddleBrown", "DarkSeaGreen",
    "LightGreen", "MediumPurple", "DarkViolet", "PaleGreen", "DarkOrchid", "YellowGreen", "Sienna",
    "Brown", "DarkGray", "DarkGrey", "LightBlue", "GreenYellow", "PaleTurquoise", "LightSteelBlue",
    "PowderBlue", "FireBrick", "DarkGoldenRod", "MediumOrchid", "RosyBrown", "DarkKhaki", "Silver",
    "MediumVioletRed", "IndianRed ", "Peru", "Chocolate", "Tan", "LightGray", "LightGrey", "Thistle",
    "Orchid", "GoldenRod", "PaleVioletRed", "Crimson", "Gainsboro", "Plum", "BurlyWood", "LightCyan",
    "Lavender", "DarkSalmon", "Violet", "PaleGoldenRod", "LightCoral", "Khaki", "AliceBlue", "HoneyDew",
    "Azure", "SandyBrown", "Wheat", "Beige", "WhiteSmoke", "MintCream", "GhostWhite", "Salmon", "AntiqueWhite",
    "Linen", "LightGoldenRodYellow", "OldLace", "Red", "Fuchsia", "Magenta", "DeepPink", "OrangeRed", "Tomato",
    "HotPink", "Coral", "DarkOrange", "LightSalmon", "Orange", "LightPink", "Pink", "Gold", "PeachPuff",
    "NavajoWhite", "Moccasin", "Bisque", "MistyRose", "BlanchedAlmond", "PapayaWhip", "LavenderBlush",
    "SeaShell", "Cornsilk", "LemonChiffon", "FloralWhite", "Snow", "Yellow", "LightYellow", "Ivory", "Black"
]

FONT_DIR = "Userbot/fontq"
FALLBACK_FONTS = [
    "NotoSans-Regular.ttf",
    "NotoColorEmoji.ttf",
    "NotoSansSymbols-Regular.ttf",
    "DejaVuSans.ttf",
    "ArialUnicodeMS.ttf"
]

def hex_to_rgb(color):
    try:
        return ImageColor.getrgb(color)
    except Exception:
        return (255, 255, 255)

def is_dark(rgb):
    r, g, b = rgb
    brightness = ((r * 299) + (g * 587) + (b * 114)) / 1000
    return brightness < 128

def find_font_that_can_render(text, preferred_fonts, size=36):
    """
    Return the first font in preferred_fonts that can render all chars in text.
    If not found, return the first one (last resort).
    """
    for fontfile in preferred_fonts:
        font_path = os.path.join(FONT_DIR, fontfile)
        if not os.path.isfile(font_path):
            continue
        try:
            font = ImageFont.truetype(font_path, size)
            # Test if all characters renderable
            for c in text:
                try:
                    font.getmask(c)
                except Exception:
                    raise
            return font
        except Exception:
            continue
    # fallback: first available font
    for fontfile in preferred_fonts:
        font_path = os.path.join(FONT_DIR, fontfile)
        if os.path.isfile(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                continue
    # fallback: system default (may not support unicode)
    return ImageFont.load_default()

async def get_sender(m):
    if m.forward_date:
        if m.forward_sender_name:
            return 1
        elif m.forward_from:
            return m.forward_from.id
        elif m.forward_from_chat:
            return m.forward_from_chat.id
        else:
            return 1
    elif m.from_user:
        return m.from_user.id
    elif m.sender_chat:
        return m.sender_chat.id
    else:
        return 1

async def sender_name(m):
    if m.forward_date:
        if m.forward_sender_name:
            return m.forward_sender_name
        elif m.forward_from:
            return (
                f"{m.forward_from.first_name} {m.forward_from.last_name or ''}"
                if m.forward_from.last_name
                else m.forward_from.first_name
            )
        elif m.forward_from_chat:
            return m.forward_from_chat.title
        else:
            return ""
    elif m.from_user:
        if m.from_user.last_name:
            return f"{m.from_user.first_name} {m.from_user.last_name or ''}"
        else:
            return m.from_user.first_name
    elif m.sender_chat:
        return m.sender_chat.title
    else:
        return ""

async def t_or_c(m):
    if m.text:
        return m.text
    elif m.caption:
        return m.caption
    else:
        return ""

async def quotly(messages, kolor, is_reply, font=None, client=None):
    if font is None:
        return await quotly_api(messages, kolor, is_reply)
    if not isinstance(messages, list):
        messages = [messages]
    # Ambil nama user dan text
    user = await sender_name(messages[0])
    text = await t_or_c(messages[0])

    # Font nama user: cari font unicode support yg bisa render seluruh nama user
    font_size_user = 34
    font_user = find_font_that_can_render(
        user,
        FALLBACK_FONTS,
        size=font_size_user
    )

    # Font text: pakai font setting user, fallback ke universal unicode
    font_size_text = 36
    preferred_fontfiles = [font] + FALLBACK_FONTS if font else FALLBACK_FONTS
    font_text = find_font_that_can_render(
        text,
        preferred_fontfiles,
        size=font_size_text
    )

    # Ukur
    dummy_img = Image.new("RGB", (1200, 1200))
    draw = ImageDraw.Draw(dummy_img)
    user_w, user_h = draw.textsize(user, font=font_user)
    text_w, text_h = draw.multiline_textsize(text, font=font_text)
    padding = 48
    line_space = 16
    img_w = max(user_w, text_w) + padding * 2
    img_h = user_h + text_h + padding * 2 + line_space
    bg_color = kolor if kolor in loanjing else "white"
    rgb_bg = hex_to_rgb(bg_color)
    font_color = (255,255,255) if is_dark(rgb_bg) else (0,0,0)
    image = Image.new("RGBA", (img_w, img_h), (0,0,0,0))
    draw = ImageDraw.Draw(image)
    radius = 48
    try:
        draw.rounded_rectangle([(0, 0), (img_w, img_h)], radius=radius, fill=rgb_bg)
    except Exception:
        draw.rectangle([(0,0),(img_w,img_h)], fill=rgb_bg)
    # Nama user
    draw.text(
        (padding, padding), user, font=font_user, fill=font_color
    )
    # Text
    draw.multiline_text(
        (padding, padding + user_h + line_space), text, font=font_text, fill=font_color, spacing=6, align="left"
    )
    output = BytesIO()
    image.save(output, format="WEBP")
    output.seek(0)
    return output.read()

async def quotly_api(messages, kolor, is_reply):
    if not isinstance(messages, list):
        messages = [messages]
    payload = {
        "type": "quote",
        "format": "png",
        "backgroundColor": kolor,
        "messages": [],
    }
    for m in messages:
        m_dict = {}
        if m.entities:
            m_dict["entities"] = [
                {
                    "type": entity.type.name.lower(),
                    "offset": entity.offset,
                    "length": entity.length,
                }
                for entity in m.entities
            ]
        elif m.caption_entities:
            m_dict["entities"] = [
                {
                    "type": entity.type.name.lower(),
                    "offset": entity.offset,
                    "length": entity.length,
                }
                for entity in m.caption_entities
            ]
        else:
            m_dict["entities"] = []
        m_dict["chatId"] = await get_sender(m)
        m_dict["text"] = await t_or_c(m)
        m_dict["avatar"] = True
        m_dict["from"] = {}
        m_dict["from"]["id"] = await get_sender(m)
        m_dict["from"]["name"] = await sender_name(m)
        m_dict["from"]["username"] = ""
        m_dict["from"]["type"] = m.chat.type.name.lower()
        m_dict["from"]["photo"] = ""
        if m.reply_to_message and is_reply:
            m_dict["replyMessage"] = {
                "name": await sender_name(m.reply_to_message),
                "text": await t_or_c(m.reply_to_message),
                "chatId": await get_sender(m.reply_to_message),
            }
        else:
            m_dict["replyMessage"] = {}
        payload["messages"].append(m_dict)
    r = await fetch.post("https://bot.lyo.su/quote/generate.png", json=payload)
    if not r.is_error:
        return r.read()
    else:
        raise QuotlyException(r.json())

def isArgInt(txt) -> list:
    count = txt
    try:
        count = int(count)
        return [True, count]
    except ValueError:
        return [False, 0]
