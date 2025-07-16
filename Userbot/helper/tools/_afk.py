import asyncio
from time import time

from ..database import dB
from ._logs import Emojik
from ._misc import ReplyCheck

class AFK_:
    def __init__(self, client, message, reason=""):
        self.client = client
        self.message = message
        self.reason = reason
        self.emo = Emojik(self.client)
        self.emo.initialize()

    async def set_afk(self):
        db_afk = {"time": time(), "reason": self.reason}
        msg_afk = f"{self.emo.sukses} **AFK MODE!**\n Reason: {self.reason}" if self.reason else "Currently AFK!!"
        # Simpan informasi media jika reply ke pesan media
        if self.message.reply_to_message:
            reply = self.message.reply_to_message
            for jenis in ["photo", "sticker", "animation", "video", "document"]:
                media = getattr(reply, jenis, None)
                if media:
                    db_afk["media_type"] = jenis
                    db_afk["media_file_id"] = media.file_id
                    break
        dB.set_var(self.client.me.id, "AFK", db_afk)
        try:
            # Kirim balasan afk beserta media jika ada
            if "media_type" in db_afk and "media_file_id" in db_afk:
                jenis = db_afk["media_type"]
                file_id = db_afk["media_file_id"]
                if jenis == "photo":
                    ae = await self.message.reply_photo(photo=file_id, caption=msg_afk)
                elif jenis == "sticker":
                    ae = await self.message.reply_sticker(sticker=file_id)
                    await self.message.reply(msg_afk, disable_web_page_preview=True)
                elif jenis == "animation":
                    ae = await self.message.reply_animation(animation=file_id, caption=msg_afk)
                elif jenis == "video":
                    ae = await self.message.reply_video(video=file_id, caption=msg_afk)
                elif jenis == "document":
                    ae = await self.message.reply_document(document=file_id, caption=msg_afk)
                else:
                    ae = await self.message.reply(msg_afk, disable_web_page_preview=True)
            else:
                ae = await self.message.reply(msg_afk, disable_web_page_preview=True)
            await asyncio.sleep(5)
            return await ae.delete()
        except Exception:
            return

    async def get_afk(self):
        vars = dB.get_var(self.client.me.id, "AFK")
        if vars:
            afk_reason = vars.get("reason")
            afk_text = f"{self.emo.sukses} **AFK MODE!**\n **Reason:** {afk_reason}" if afk_reason else "Currently AFK!!"
            try:
                # Kirim balasan media jika ada
                if "media_type" in vars and "media_file_id" in vars:
                    jenis = vars["media_type"]
                    file_id = vars["media_file_id"]
                    if jenis == "photo":
                        ae = await self.message.reply_photo(photo=file_id, caption=afk_text)
                    elif jenis == "sticker":
                        ae = await self.message.reply_sticker(sticker=file_id)
                        await self.message.reply(afk_text, disable_web_page_preview=True)
                    elif jenis == "animation":
                        ae = await self.message.reply_animation(animation=file_id, caption=afk_text)
                    elif jenis == "video":
                        ae = await self.message.reply_video(video=file_id, caption=afk_text)
                    elif jenis == "document":
                        ae = await self.message.reply_document(document=file_id, caption=afk_text)
                    else:
                        ae = await self.message.reply(afk_text, disable_web_page_preview=True)
                else:
                    ae = await self.message.reply(afk_text, disable_web_page_preview=True)
                await asyncio.sleep(5)
                return await ae.delete()
            except Exception:
                return

    async def unset_afk(self):
        vars = dB.get_var(self.client.me.id, "AFK")
        if vars:
            dB.remove_var(self.client.me.id, "AFK")
            afk_text = f"<b>{self.emo.sukses} Back to Online!!"
            try:
                ae = await self.message.reply(afk_text)
                await asyncio.sleep(3)
                return await ae.delete()
            except Exception:
                return
