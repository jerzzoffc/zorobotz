from pyrogram.enums import ParseMode
from Userbot.helper.database import dB

async def broadcast_to_clients(bot, text, exclude_id=None):
    """
    Kirim broadcast ke semua client yang pernah /start (data di dB var BROADCAST).
    exclude_id: user id yang ingin dikecualikan (optional)
    """
    brod = dB.get_list_from_var(bot.me.id, "BROADCAST")
    for uid in brod:
        if exclude_id and uid == exclude_id:
            continue
        try:
            await bot.send_message(uid, text)
        except Exception:
            continue
