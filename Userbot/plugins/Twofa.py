from pyrogram.errors import MessageTooLong

from config import botcax_api
from Userbot.helper.tools import Emojik, get, h_s, initial_ctext, zb, paste

__MODULES__ = "TwoFATools"

def help_string(org):
    return h_s(org, "help_twofactor")

@zb.ubot("tfa")
async def _(client, message, _):
    em = Emojik(client)
    em.initialize()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = initial_ctext(client)
    prs = await message.reply_text(_("proses").format(em.proses, proses_))
    rep = message.reply_to_message
    if len(message.command) < 2 and not rep:
        await prs.edit(
            f"{em.gagal}**Silahkan berikan token 2FA atau balas ke pesan yang berisi token.!!**"
        )
        return
    # Ambil argumen/token dari reply atau command args
    if rep and rep.text:
        token = rep.text.strip()
    else:
        token = client.get_arg(message).strip()
    url = f"https://api.botcahx.eu.org/api/tools/2fa?token={token}&apikey={botcax_api}"
    respon = await get(url)
    if respon.get("status") is True:
        data = respon.get("result", {})
        code = data.get("token")
        # Gunakan <code> agar mudah dicopy dan inline
        msg = (
            f"{em.sukses}<b>2FA Token:</b> <code>{code}</code>"
        )
        try:
            await prs.edit(msg, disable_web_page_preview=True)
        except MessageTooLong:
            await prs.delete()
            konten = str(msg)
            link = await paste(konten)
            await message.reply(
                f"{em.sukses}**[Klik Disini]({link}) Untuk Melihat 2FA Token.**",
                disable_web_page_preview=True,
            )
        # Hapus perintah user
        await message.delete()
    else:
        error_msg = respon.get("message", "Maaf!! Sepertinya server sedang error!")
        await prs.edit(f"{em.gagal}**{error_msg}**")
        await message.delete()
