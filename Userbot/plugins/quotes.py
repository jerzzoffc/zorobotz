################################################################
"""
 Mix-Userbot Open Source . Maintained by userbor13
 Plugin: QuotLy - Generate quote stickers via @QuotLyBot

 @CREDIT: Adapted by Copilot from user example
"""
################################################################

import asyncio
import os

from pyrogram.raw.functions.messages import DeleteHistory
from pyrogram.errors import UsernameInvalid

from Userbot import nlx
from Userbot.helper.tools import Emojik, h_s, initial_ctext, zb

__MODULES__ = "QuotLy"

def help_string(org):
    return h_s(org, "help_quotly")

@zb.ubot("q")
async def _(c: nlx, m, _):
    em = Emojik(c)
    em.initialize()
    prs = em.proses
    brhsl = em.sukses
    ggl = em.gagal
    info = await m.reply(f"{prs}proceꜱꜱing...", quote=True)
    await c.unblock_user("@QuotLyBot")
    if m.reply_to_message:
        if len(m.command) < 2:
            msg = [m.reply_to_message]
        else:
            try:
                count = int(m.command[1])
            except Exception as error:
                return await info.edit(str(error))
            msg = [
                i
                for i in await c.get_messages(
                    chat_id=m.chat.id,
                    message_ids=range(
                        m.reply_to_message.id, m.reply_to_message.id + count
                    ),
                    replies=-1,
                )
            ]
        try:
            for x in msg:
                await x.forward("@QuotLyBot")
        except Exception:
            pass
        await asyncio.sleep(9)
        await info.delete()
        async for quotly in c.get_chat_history("@QuotLyBot", limit=1):
            if not quotly.sticker:
                await m.reply(
                    f"@QuotLyBot {ggl}tidak dapat merespon permintaan", quote=True
                )
            else:
                sticker = await c.download_media(quotly)
                await m.reply_sticker(sticker, quote=True)
                os.remove(sticker)
    else:
        if len(m.command) < 2:
            return await info.edit(f"{ggl}reply to text/media")
        else:
            msg = await c.send_message(
                "@QuotLyBot", f"/qcolor {m.command[1]}"
            )
            await asyncio.sleep(1)
            get = await c.get_messages("@QuotLyBot", msg.id + 1)
            await info.edit(
                f"{brhsl}warna latar belakang kutipan disetel ke: {get.text.split(':')[1]}"
            )
    try:
        user_info = await c.resolve_peer("@QuotLyBot")
        return await c.invoke(DeleteHistory(peer=user_info, max_id=0, revoke=True))
    except:
        pass
