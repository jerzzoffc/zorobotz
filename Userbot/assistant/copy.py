import asyncio
from Userbot import bot, nlx
from Userbot.helper.tools import zb
from Userbot.plugins.copy_con import gas_download

@zb.bots("copy")
async def _(c: bot, m, _):
    if m.from_user.id not in nlx._my_id:
        return
    xx = await m.reply("Tunggu Sebentar...")
    links = c.get_arg(m)
    if not links:
        return await xx.edit(f"<b><code>{m.text}</code> [link]</b>")
    link_list = [l.strip() for l in links.split(",") if l.strip()]
    if not link_list:
        return await xx.edit(f"<b><code>{m.text}</code> [link]</b>")
    total = 0
    failed = 0
    for link in link_list:
        if link.startswith(("https", "t.me")):
            try:
                msg_id = int(link.split("/")[-1])
                if "t.me/c/" in link:
                    chat = int("-100" + str(link.split("/")[-2]))
                else:
                    chat = str(link.split("/")[-2])
                try:
                    g = await c.get_messages(chat, msg_id)
                    try:
                        await g.copy(m.chat.id)
                        total += 1
                    except Exception:
                        try:
                            await gas_download(g, c, xx, m)
                            total += 1
                        except Exception:
                            failed += 1
                except Exception:
                    failed += 1
            except Exception:
                failed += 1
        else:
            failed += 1
        await asyncio.sleep(1)
    await xx.edit(f"✅ <b>Berhasil copy {total} pesan dari {len(link_list)} link.</b>\n❌ Gagal: {failed} link.")
