import asyncio
from datetime import datetime

from pyrogram.errors import FloodWait
from Userbot import nlx
from Userbot.helper.database import dB
from Userbot.helper.tools import h_s, zb

__MODULES__ = "JasebDb"

def help_string(org):
    return h_s(org, "help_jasebdb")

#creator : @moire_mor
# --- GROUP CLUSTER LIST (You can edit/expand this) ---
GROUP_CLUSTERS = ["group1", "group2", "group3", "group4", "group5"]

def help_string(org):
    return h_s(org, "help_jasebdb")

def get_bc_group_list(user_id, group_name):
    key = f"BC_TARGET_GROUPS_{group_name}"
    return dB.get_list_from_var(user_id, key) or []

@zb.ubot("jasebx")
async def jaseb_handler(client, message, _):
    user_id = client.me.id

    if len(message.command) < 2:
        return await message.reply(
            "<blockquote><b><emoji id=5319112319429523945>⛔️</emoji> Perintah tidak lengkap!</b></blockquote>\n"
            "<blockquote><b><emoji id=5316554554735607106>⚠️</emoji> Silakan cek help modul Jaseb Db.</b></blockquote>"
        )

    action = message.command[1].lower()

    # --- Watermark ON/OFF ---
    if action == "wm":
        if len(message.command) < 3 or message.command[2].lower() not in ["on", "off"]:
            return await message.reply(
                "<code>jasebx wm on/off</code> untuk mengaktifkan/menonaktifkan watermark broadcast."
            )
        status = message.command[2].lower() == "on"
        dB.set_var(user_id, "BC_WM_ENABLED", status)
        await message.reply(
            f"<b>Watermark broadcast {'diaktifkan' if status else 'dinonaktifkan'}.</b>"
        )
        return

    # --- Set Watermark ---
    if action == "setwm":
        if not message.reply_to_message:
            return await message.reply(
                "<code>Balas ke pesan yang ingin dijadikan watermark, lalu gunakan perintah ini.</code>"
            )
        wm_text = None
        if message.reply_to_message.text:
            wm_text = message.reply_to_message.text
        elif message.reply_to_message.caption:
            wm_text = message.reply_to_message.caption
        else:
            return await message.reply("<code>Pesan watermark harus berupa text/caption.</code>")
        dB.set_var(user_id, "BC_WM_TEXT", wm_text)
        await message.reply("<b>Watermark broadcast berhasil disimpan.</b>")
        return
#@moire_mor
    # Tambah group ke cluster
    if action == "addbcgb":
        if len(message.command) < 3:
            return await message.reply(
                "Gunakan format: <code>jasebx addbcgb group1 [id_group/@username]</code>"
            )

        group_name = message.command[2].lower()
        if group_name not in GROUP_CLUSTERS:
            return await message.reply(f"Kelompok <b>{group_name}</b> tidak terdaftar.")

        key = f"BC_TARGET_GROUPS_{group_name}"

        # Cari id group target
        group_id = None
        if len(message.command) < 4:
            if message.chat.type in ["group", "supergroup"]:
                group_id = message.chat.id
            else:
                return await message.reply(
                    "<code>jasebx addbcgb groupX [id_group/@username]</code>"
                )
        else:
            arg = message.command[3]
            if arg.startswith("@"):
                try:
                    group_entity = await client.get_chat(arg)
                    group_id = group_entity.id
                except Exception as e:
                    return await message.reply(
                        f"Gagal menemukan group dengan username {arg}: {e}"
                    )
            elif arg.lstrip("-").isdigit():
                group_id = int(arg)
            else:
                return await message.reply(
                    "Format salah! Gunakan: <code>jasebx addbcgb groupX [id_group/@username]</code>"
                )

        group_list = dB.get_list_from_var(user_id, key) or []
        if group_id in group_list:
            return await message.reply(
                "Group sudah ada di daftar target kelompok ini."
            )
        dB.add_to_var(user_id, key, group_id)
        return await message.reply(
            f"Group <code>{group_id}</code> ditambahkan ke daftar target broadcast cluster <b>{group_name}</b>."
        )

    # Hapus group dari cluster
    elif action == "delbcgb":
        if len(message.command) < 4 or not message.command[3].lstrip("-").isdigit():
            return await message.reply("Gunakan format: <code>jasebx delbcgb group1 id_group</code>")
        group_name = message.command[2].lower()
        if group_name not in GROUP_CLUSTERS:
            return await message.reply(f"Group Culster <b>{group_name}</b> tidak terdaftar.")
        key = f"BC_TARGET_GROUPS_{group_name}"
        group_id = int(message.command[3])
        group_list = dB.get_list_from_var(user_id, key) or []
        if group_id not in group_list:
            return await message.reply("Group tidak ada di daftar target group cluster ini.")
        dB.rm_from_var(user_id, key, group_id)
        return await message.reply(
            f"Group <code>{group_id}</code> dihapus dari group cluster <b>{group_name}</b>."
        )
#@moire_mor
    # List group target pada cluster
    elif action == "listbcgb":
        if len(message.command) < 3:
            return await message.reply("Gunakan format: <code>jasebx listbcgb group1</code>")
        group_name = message.command[2].lower()
        if group_name not in GROUP_CLUSTERS:
            return await message.reply(f"Cluster <b>{group_name}</b> tidak terdaftar.")
        group_list = get_bc_group_list(user_id, group_name)
        if not group_list:
            return await message.reply(f"Daftar group target <b>{group_name}</b> kosong.")
        msg = f"Daftar group target di <b>{group_name}</b>:\n\n"
        for gid in group_list:
            try:
                chat = await client.get_chat(gid)
                if chat.username:
                    link = f"https://t.me/{chat.username}"
                    name = f'<a href="{link}">{chat.title}</a>'
                else:
                    # Jika tidak ada username, gunakan tg:// link
                    name = f'<a href="tg://resolve?domain={gid}">{chat.title}</a>'
            except Exception:
                name = "<i>(Group tidak ditemukan)</i>"
            msg += f"• {name} <code>[{gid}]</code>\n"
        return await message.reply(msg, disable_web_page_preview=True)

    # List semua cluster beserta jumlah group target: listgbcluster
    elif action == "listgbcluster":
        msg = "<b>Daftar Cluster Group Broadcast:</b>\n"
        found = False
        for cluster in GROUP_CLUSTERS:
            glist = get_bc_group_list(user_id, cluster)
            msg += f"• <b>{cluster}</b>: {len(glist)} group\n"
            if glist:
                found = True
        if not found:
            msg += "\n<code>Belum ada group target di cluster manapun.</code>"
        return await message.reply(msg)

    # Broadcast ke cluster tertentu
    elif action == "broadcast":
        if len(message.command) < 3:
            return await message.reply("Gunakan format: <code>jasebx broadcast group1</code>")
        group_name = message.command[2].lower()
        if group_name not in GROUP_CLUSTERS:
            return await message.reply(f"Cluster <b>{group_name}</b> tidak terdaftar.")
        key = f"BC_TARGET_GROUPS_{group_name}"

        if not dB.get_var(user_id, "ENABLED"):
            return await message.reply(
                "<blockquote><b><emoji id=4918014360267260850>⛔️</emoji> Modul nonaktif!</b>\n"
                " └<i> Aktifkan dengan perintah : jasebx on</i></blockquote>"
            )
#@moire_mor
        bc_groups = get_bc_group_list(user_id, group_name)
        if not bc_groups:
            return await message.reply(
                f"<blockquote><b><emoji id=4918014360267260850>⛔️</emoji> Tidak ada group target di <b>{group_name}</b>!</b></blockquote>"
            )

        client.status_background[user_id] = True

        if not message.reply_to_message:
            return await message.reply(
                "<blockquote><b><emoji id=4918014360267260850>⛔️</emoji> Pesan tidak ditemukan!</b>\n"
                " └<i> Balas ke pesan yang ingin di-broadcast</i></blockquote>"
            )

        msg = f"<blockquote><i><emoji id=5316571734604790521>🚀</emoji> Proses broadcast ke <b>{group_name}</b> sedang berjalan...</i></blockquote>"
        status_msg = await message.reply(msg)

        dB.set_var(user_id, f"MESSAGE_IDS_{group_name}", {
            "chat_id": message.chat.id,
            "message_id": message.reply_to_message.id
        })
        dB.set_var(user_id, f"BC_RUNNING_{group_name}", True)

        await status_msg.edit(
            msg + "\n<blockquote><i><emoji id=5316554554735607106>⚠️</emoji> Pesan yang di reply jangan sampai dihapus siapapun.\nKalau dihapus broadcast mu error jika ubot restart.</i></blockquote>"
        )

        blacklist = dB.get_list_from_var(user_id, "BLGCAST")
        delay_gcast = float(dB.get_var(user_id, "DELAY_GCAST") or 0.5)
        interval_delay = float(dB.get_var(user_id, "DELAY_PER_SEND") or 0.5)
        auto_off = dB.get_var(user_id, "AUTO-OFF")
        max_iterations = int(dB.get_var(user_id, "MAX_LOOP") or 999999999)

        putaran = int(dB.get_var(user_id, f'INTERVAL_COUNT_{group_name}') or 0)

        # Pastikan boolean
        wm_enabled = bool(dB.get_var(user_id, "BC_WM_ENABLED"))
        wm_text = dB.get_var(user_id, "BC_WM_TEXT")

        while putaran < max_iterations:
            if (
                not dB.get_var(user_id, "ENABLED")
                or not client.status_background.get(user_id)
                or not dB.get_var(user_id, f"BC_RUNNING_{group_name}")
            ):
                client.status_background[user_id] = False
                dB.set_var(user_id, f"MESSAGE_IDS_{group_name}", {})
                break

            done, failed = 0, 0

            for chat_id in bc_groups:
                if (
                    not dB.get_var(user_id, "ENABLED")
                    or not client.status_background.get(user_id)
                    or not dB.get_var(user_id, f"BC_RUNNING_{group_name}")
                ):
                    client.status_background[user_id] = False
                    dB.set_var(user_id, f"MESSAGE_IDS_{group_name}", {})
                    break

                if chat_id in blacklist:
                    continue
#@moire_mor
                try:
                    if wm_enabled and wm_text:
                        # --- TEXT ONLY ---
                        if message.reply_to_message.text and not message.reply_to_message.media:
                            # Gabungkan watermark, pertahankan format asli
                            orig_text = message.reply_to_message.text
                            orig_entities = message.reply_to_message.entities
                            send_text = f"{orig_text}\n\n{wm_text}"
                            # entities hanya untuk bagian pesan asli, watermark tanpa entitas
                            await client.send_message(
                                chat_id,
                                send_text,
                                entities=orig_entities
                            )
                        # --- MEDIA + CAPTION ---
                        elif message.reply_to_message.caption and message.reply_to_message.media:
                            orig_caption = message.reply_to_message.caption
                            orig_entities = message.reply_to_message.caption_entities
                            send_caption = f"{orig_caption}\n\n{wm_text}"
                            await client.send_document(
                                chat_id,
                                document=message.reply_to_message.document.file_id if message.reply_to_message.document else None,
                                photo=message.reply_to_message.photo.file_id if message.reply_to_message.photo else None,
                                video=message.reply_to_message.video.file_id if message.reply_to_message.video else None,
                                audio=message.reply_to_message.audio.file_id if message.reply_to_message.audio else None,
                                caption=send_caption,
                                caption_entities=orig_entities
                            )
                        else:
                            await message.reply_to_message.forward(chat_id)
                    else:
                        # Watermark off: kirim pesan asli (text/caption/media) seperti forward biasa
                        if message.reply_to_message.text and not message.reply_to_message.media:
                            await client.send_message(
                                chat_id,
                                message.reply_to_message.text,
                                entities=message.reply_to_message.entities
                            )
                        elif message.reply_to_message.caption and message.reply_to_message.media:
                            await client.send_document(
                                chat_id,
                                document=message.reply_to_message.document.file_id if message.reply_to_message.document else None,
                                photo=message.reply_to_message.photo.file_id if message.reply_to_message.photo else None,
                                video=message.reply_to_message.video.file_id if message.reply_to_message.video else None,
                                audio=message.reply_to_message.audio.file_id if message.reply_to_message.audio else None,
                                caption=message.reply_to_message.caption,
                                caption_entities=message.reply_to_message.caption_entities
                            )
                        else:
                            await message.reply_to_message.forward(chat_id)
                    done += 1
                    await asyncio.sleep(delay_gcast)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                except Exception:
                    failed += 1
#@moire_mor
            putaran += 1
            dB.set_var(user_id, f'INTERVAL_COUNT_{group_name}', putaran)

            result_msg = f"""
<blockquote><b><emoji id=5350404703823883106>⭐️</emoji> Hasil Broadcast ke <b>{group_name}</b></b></blockquote>
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
            saved_msg_data = dB.get_var(user_id, f"MESSAGE_IDS_{group_name}")
            await client.send_message(saved_msg_data["chat_id"], result_msg)
            await asyncio.sleep(int(interval_delay) * 60)

    # -- SISANYA Tetap sama (on, off, delay, interval, setday, status, time, dst) --
    elif action == "on":
        dB.set_var(user_id, "ENABLED", True)
        await message.reply(
            "<blockquote><b><emoji id=4916036072560919511>✅</emoji> Modul Jaseb Db telah diaktifkan!</b>\n └<i> Status: Online dan siap digunakan</i></blockquote>"
        )

    elif action == "off":
        client.status_background[user_id] = False
        dB.set_var(user_id, "ENABLED", False)
        # Bersihkan flag BC_RUNNING semua cluster
        for cluster in GROUP_CLUSTERS:
            dB.set_var(user_id, f"BC_RUNNING_{cluster}", False)
        await message.reply(
            "<blockquote><b><emoji id=4918014360267260850>⛔️</emoji> Modul Jaseb Db telah dinonaktifkan!</b>\n └<i> Status: Offline</i></blockquote>"
        )

    elif action == "delay":
        if len(message.command) < 3 or not message.command[2].replace(".", "", 1).isdigit():
            return await message.reply(
                "<blockquote><b><emoji id=4918014360267260850>⛔️</emoji> Format tidak valid!</b>\n└<i> Masukkan angka untuk delay (detik)</i></blockquote>"
            )
        dB.set_var(user_id, "DELAY_GCAST", float(message.command[2]))
        await message.reply(
            f"<blockquote><b><emoji id=4916036072560919511>✅</emoji> Delay disimpan!</b>\n └<i> {message.command[2]} detik/grup</i></blockquote>"
        )

    elif action == "interval":
        if len(message.command) < 3 or not message.command[2].replace(".", "", 1).isdigit():
            return await message.reply(
                "<blockquote><b><emoji id=4918014360267260850>⛔️</emoji> Format tidak valid!</b>\n└<i> Masukkan angka untuk interval (menit)</i></blockquote>"
            )
        dB.set_var(user_id, "DELAY_PER_SEND", float(message.command[2]))
        await message.reply(
            f"<blockquote><b><emoji id=4916036072560919511>✅</emoji> Interval disimpan!</b>\n └<i> {message.command[2]} menit</i></blockquote>"
        )

    elif action == "setday":
        if len(message.command) < 3:
            return await message.reply(
                "<blockquote><b><emoji id=4918014360267260850>⛔️</emoji> Format tidak valid!</b>\n └<i> Gunakan: jaseb setday DD/MM/YYYY</i></blockquote>"
            )
        if client.parse_date(message.command[2]):
            dB.set_var(user_id, "AUTO-OFF", message.command[2])
            await message.reply(
                f"<blockquote><b><emoji id=5352848733488834757>✔️</emoji> Auto-off diatur ke {message.command[2]}</b></blockquote>"
            )
        else:
            await message.reply(
                "<blockquote><b><emoji id=4918014360267260850>⛔️</emoji> Format tanggal salah!</b>\n └<i> Gunakan DD/MM/YYYY</i></blockquote>"
            )

    elif action == "status":
        delay_gcast = float(dB.get_var(user_id, "DELAY_GCAST") or 0.5)
        interval_delay = float(dB.get_var(user_id, "DELAY_PER_SEND") or 0.5)
        max_iterations = int(dB.get_var(user_id, "MAX_LOOP") or 999999999)
        auto_off = dB.get_var(user_id, "AUTO-OFF")
        # Total target di semua cluster
        total = sum(len(get_bc_group_list(user_id, c)) for c in GROUP_CLUSTERS)
        await message.reply(
            f"""<blockquote><b><emoji id=5350404703823883106>⭐️</emoji> Status Modul Jaseb Db <emoji id=5350404703823883106>⭐️</emoji></b></blockquote>
<blockquote>╭─❖ Info Pengaturan
├ <emoji id=5317059204802952215>🖱️</emoji> Status : {'🟢 Online' if client.status_background.get(user_id) else '🔴 Offline'}
├ <emoji id=5317059204802952215>🖱️</emoji> Delay : {delay_gcast}s/grup
├ <emoji id=5317059204802952215>🖱️</emoji> Interval Delay : {interval_delay}m
├ <emoji id=5317059204802952215>🖱️</emoji> Interval ke : {dB.get_var(user_id, 'INTERVAL_COUNT_group1') or 0}
├ <emoji id=5317059204802952215>🖱️</emoji> Auto-off : {auto_off}
├ <emoji id=5317059204802952215>🖱️</emoji> Total Target Group : {total} grup (di semua cluster)
└ <emoji id=5317059204802952215>🖱️</emoji> TimeNow Server : {datetime.now().strftime('%d/%m/%Y')}</blockquote>"""
        )

    elif action == "time":
        await message.reply(
            f"<blockquote><b><emoji id=5350595795508814391>🕓</emoji> Waktu Server Saat Ini</b>\n └<i> <code>{datetime.now().strftime('%d/%m/%Y %H:%M')}</code></i></blockquote>"
        )

    else:
        await message.reply(
            """<blockquote><b><emoji id=4918014360267260850>⛔️</emoji> Perintah tidak valid!</b></blockquote>
<blockquote><b><emoji id=5350666288807046023>⚙️</emoji> Gunakan perintah berikut:</b>
<i>• <emoji id=5317059204802952215>🖱️</emoji> jasebx on - Aktifkan modul</i>
<i>• <emoji id=5317059204802952215>🖱️</emoji> jasebx off - Nonaktifkan modul</i>
<i>• <emoji id=5317059204802952215>🖱️</emoji> jasebx delay <angka> - Atur delay</i>
<i>• <emoji id=5317059204802952215>🖱️</emoji> jasebx interval <angka> - Atur interval</i>
<i>• <emoji id=5317059204802952215>🖱️</emoji> jasebx setday <tgl> - Auto-off</i>
<i>• <emoji id=5317059204802952215>🖱️</emoji> jasebx status - Cek status</i>
<i>• <emoji id=5317059204802952215>🖱️</emoji> jasebx time - Waktu server</i>
<i>• <emoji id=5317059204802952215>🖱️</emoji> jasebx broadcast group1 - Kirim pesan ke group target cluster group1</i>
<i>• <emoji id=5317059204802952215>🖱️</emoji> jasebx addbcgb group1 [id_group/@username] - Tambah group target cluster group1</i>
<i>• <emoji id=5317059204802952215>🖱️</emoji> jasebx delbcgb group1 id_group - Hapus group target cluster group1</i>
<i>• <emoji id=5317059204802952215>🖱️</emoji> jasebx listbcgb group1 - List group target cluster group1</i>
<i>• <emoji id=5317059204802952215>🖱️</emoji> jasebx listgbcluster - List semua cluster & jumlah group target</i>
<i>• <emoji id=5317059204802952215>🖱️</emoji> jasebx wm on/off - Aktif/nonaktif watermark broadcast</i>
<i>• <emoji id=5317059204802952215>🖱️</emoji> jasebx setwm <reply pesan> - Set watermark broadcast</i></blockquote>"""
            )
