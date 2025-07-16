import asyncio
from datetime import datetime

from pyrogram.errors import FloodWait
from Userbot import nlx
from Userbot.helper.database import dB
from Userbot.helper.tools import h_s, zb

__MODULES__ = "JasebDay"

def help_string(org):
    return h_s(org, "help_jasebday")
#creator : @moire_mor


@zb.ubot("jaseb")
async def jaseb_handler(client, message, _):
    user_id = client.me.id

    if len(message.command) < 2:
        return await message.reply(
            "<blockquote><b><emoji id=5319112319429523945>⛔️</emoji> Perintah tidak lengkap!</b></blockquote>\n"
            "<blockquote><b><emoji id=5316554554735607106>⚠️</emoji> Silakan cek help modul Jaseb.</b></blockquote>"
        )

    action = message.command[1].lower()

    if action == "on":
        dB.set_var(user_id, "ENABLED", True)
        await message.reply("<blockquote><b><emoji id=4916036072560919511>✅</emoji> Modul Jaseb telah diaktifkan!</b>\n └<i> Status: Online dan siap digunakan</i></blockquote>")

    elif action == "off":
        client.status_background[user_id] = False
        dB.set_var(user_id, "ENABLED", False)
        dB.set_var(user_id, "INTERVAL_COUNT", 0)
        dB.set_var(user_id, "MESSAGE_IDS", {})
        await message.reply("<blockquote><b><emoji id=4918014360267260850>⛔️</emoji> Modul Jaseb telah dinonaktifkan!</b>\n └<i> Status: Offline</i></blockquote>")

    elif action == "delay":
        if len(message.command) < 3 or not message.command[2].replace(".", "", 1).isdigit():
            return await message.reply("<blockquote><b><emoji id=4918014360267260850>⛔️</emoji> Format tidak valid!</b>\n└<i> Masukkan angka untuk delay (detik)</i></blockquote>")
        dB.set_var(user_id, "DELAY_GCAST", float(message.command[2]))
        await message.reply(f"<blockquote><b><emoji id=4916036072560919511>✅</emoji> Delay disimpan!</b>\n └<i> {message.command[2]} detik/grup</i></blockquote>")

    elif action == "interval":
        if len(message.command) < 3 or not message.command[2].replace(".", "", 1).isdigit():
            return await message.reply("<blockquote><b><emoji id=4918014360267260850>⛔️</emoji> Format tidak valid!</b>\n└<i> Masukkan angka untuk interval (menit)</i></blockquote>")
        dB.set_var(user_id, "DELAY_PER_SEND", float(message.command[2]))
        await message.reply(f"<blockquote><b><emoji id=4916036072560919511>✅</emoji> Interval disimpan!</b>\n └<i> {message.command[2]} menit</i></blockquote>")

    elif action == "setday":
        if len(message.command) < 3:
            return await message.reply("<blockquote><b><emoji id=4918014360267260850>⛔️</emoji> Format tidak valid!</b>\n └<i> Gunakan: jaseb setday DD/MM/YYYY</i></blockquote>")
        if client.parse_date(message.command[2]):
            dB.set_var(user_id, "AUTO-OFF", message.command[2])
            await message.reply(f"<blockquote><b><emoji id=5352848733488834757>✔️</emoji> Auto-off diatur ke {message.command[2]}</b></blockquote>")
        else:
            await message.reply("<blockquote><b><emoji id=4918014360267260850>⛔️</emoji> Format tanggal salah!</b>\n └<i> Gunakan DD/MM/YYYY</i></blockquote>")

    elif action == "status":
        delay_gcast = float(dB.get_var(user_id, "DELAY_GCAST") or 0.5)
        interval_delay = float(dB.get_var(user_id, "DELAY_PER_SEND") or 0.5)
        max_iterations = int(dB.get_var(user_id, "MAX_LOOP") or 999999999)
        auto_off = dB.get_var(user_id, "AUTO-OFF")
        await message.reply(
            f"""<blockquote><b><emoji id=5350404703823883106>⭐️</emoji> Status Modul Jaseb Day <emoji id=5350404703823883106>⭐️</emoji></b></blockquote>
<blockquote>╭─❖ Info Pengaturan
├ <emoji id=5317059204802952215>🖱️</emoji> Status : {'🟢 Online' if client.status_background.get(user_id) else '🔴 Offline'}
├ <emoji id=5317059204802952215>🖱️</emoji> Delay : {delay_gcast}s/grup
├ <emoji id=5317059204802952215>🖱️</emoji> Interval Delay : {interval_delay}m
├ <emoji id=5317059204802952215>🖱️</emoji> Interval ke : {dB.get_var(user_id, 'INTERVAL_COUNT') or 0}
├ <emoji id=5317059204802952215>🖱️</emoji> Auto-off : {auto_off}
└ <emoji id=5317059204802952215>🖱️</emoji> TimeNow Server : {datetime.now().strftime('%d/%m/%Y')}</blockquote>"""
        )
#@moire_mor
    elif action == "time":
        await message.reply(
            f"<blockquote><b><emoji id=5350595795508814391>🕓</emoji> Waktu Server Saat Ini</b>\n └<i> <code>{datetime.now().strftime('%d/%m/%Y %H:%M')}</code></i></blockquote>"
        )

    elif action == "broadcast":
        if not dB.get_var(user_id, "ENABLED"):
            return await message.reply(
                "<blockquote><b><emoji id=4918014360267260850>⛔️</emoji> Modul nonaktif!</b>\n"
                " └<i> Aktifkan dengan perintah : jaseb on</i></blockquote>"
            )

        client.status_background[user_id] = True

        if not message.reply_to_message:
            return await message.reply(
                "<blockquote><b><emoji id=4918014360267260850>⛔️</emoji> Pesan tidak ditemukan!</b>\n"
                " └<i> Balas ke pesan yang ingin di-broadcast</i></blockquote>"
            )

        msg = "<blockquote><i><emoji id=5316571734604790521>🚀</emoji> Proses broadcast sedang berjalan...</i></blockquote>"
        status_msg = await message.reply(msg)

        dB.set_var(user_id, "MESSAGE_IDS", {
            "chat_id": message.chat.id,
            "message_id": message.reply_to_message.id
        })

        await status_msg.edit(msg + "\n<blockquote><i><emoji id=5316554554735607106>⚠️</emoji> Pesan yang di reply jangan sampai dihapus siapapun.\nKalau dihapus gcast mu error jika ubot mu restart</blockquote></i>")

        chat_ids = await client.get_chats_dialog("group")
        blacklist = dB.get_list_from_var(user_id, "BLGCAST")
        delay_gcast = float(dB.get_var(user_id, "DELAY_GCAST") or 0.5)
        interval_delay = float(dB.get_var(user_id, "DELAY_PER_SEND") or 0.5)
        auto_off = dB.get_var(user_id, "AUTO-OFF")
        max_iterations = int(dB.get_var(user_id, "MAX_LOOP") or 999999999)
#@moire_mor
        putaran = int(dB.get_var(user_id, 'INTERVAL_COUNT') or 0)

        while putaran < max_iterations:
            if not dB.get_var(user_id, "ENABLED") or not client.status_background.get(user_id):
                client.status_background[user_id] = False
                dB.set_var(user_id, "MESSAGE_IDS", {})
                break

            done, failed = 0, 0

            for chat_id in chat_ids:
                if not dB.get_var(user_id, "ENABLED") or not client.status_background.get(user_id):
                    client.status_background[user_id] = False
                    dB.set_var(user_id, "MESSAGE_IDS", {})
                    break

                if chat_id in blacklist:
                    continue

                try:
                    await message.reply_to_message.forward(chat_id)
                    done += 1
                    await asyncio.sleep(delay_gcast)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                except Exception:
                    failed += 1

            putaran += 1
            dB.set_var(user_id, "INTERVAL_COUNT", putaran)

            result_msg = f"""
<blockquote><b><emoji id=5350404703823883106>⭐️</emoji> Hasil Broadcast</b></blockquote>
<blockquote>╭─❖ Ringkasan
├ <emoji id=5317059204802952215>🖱️</emoji> Status : Selesai
├ <emoji id=5317059204802952215>🖱️</emoji> Berhasil : {done} grup
├ <emoji id=5317059204802952215>🖱️</emoji> Gagal : {failed} grup
├ <emoji id=5317059204802952215>🖱️</emoji> Delay : {delay_gcast}s/grup
├ <emoji id=5317059204802952215>🖱️</emoji> Interval Delay : {int(interval_delay)}m
├ <emoji id=5317059204802952215>🖱️</emoji> Putaran Ke : {putaran}
├ <emoji id=5317059204802952215>🖱️</emoji> Auto-off : {auto_off}
└ <emoji id=5317059204802952215>🖱️</emoji> Server Time : {datetime.now().strftime('%d/%m/%Y')}</blockquote>
"""
            saved_msg_data = dB.get_var(user_id, "MESSAGE_IDS")
            await client.send_message(saved_msg_data["chat_id"], result_msg)
            await asyncio.sleep(int(interval_delay) * 60)

    else:
        await message.reply(
            """<blockquote><b><emoji id=4918014360267260850>⛔️</emoji> Perintah tidak valid!</b></blockquote>
<blockquote><b><emoji id=5350666288807046023>⚙️</emoji> Gunakan perintah berikut:</b>
<i>• <emoji id=5317059204802952215>🖱️</emoji> jaseb on - Aktifkan modul</i>
<i>• <emoji id=5317059204802952215>🖱️</emoji> jaseb off - Nonaktifkan modul</i>
<i>• <emoji id=5317059204802952215>🖱️</emoji> jaseb delay <angka> - Atur delay</i>
<i>• <emoji id=5317059204802952215>🖱️</emoji> jaseb interval <angka> - Atur interval</i>
<i>• <emoji id=5317059204802952215>🖱️</emoji> jaseb setday <tgl> - Auto-off</i>
<i>• <emoji id=5317059204802952215>🖱️</emoji> jaseb status - Cek status</i>
<i>• <emoji id=5317059204802952215>🖱️</emoji> jaseb time - Waktu server</i>
<i>• <emoji id=5317059204802952215>🖱️</emoji> jaseb broadcast - Kirim pesan</i></blockquote>"""
        )
