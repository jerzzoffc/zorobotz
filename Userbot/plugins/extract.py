import os
import zipfile
import rarfile
import time
import shutil

from pyrogram.types import InputMediaDocument
from pyrogram import filters
from Userbot.helper.tools import Emojik, initial_ctext, zb, h_s
from Userbot import nlx

pending_extract = {}

# --- AUTO CLEANUP --- #
def cleanup_old_files(
    base_dirs,
    age_seconds=3600
):
    """
    Hapus file/folder di base_dirs yang lebih tua dari age_seconds.
    """
    now = time.time()
    for base_dir in base_dirs:
        if not os.path.exists(base_dir):
            continue
        for entry in os.listdir(base_dir):
            path = os.path.join(base_dir, entry)
            try:
                mtime = os.path.getmtime(path)
                if now - mtime > age_seconds:
                    if os.path.isfile(path):
                        os.remove(path)
                    elif os.path.isdir(path):
                        shutil.rmtree(path)
            except Exception:
                pass

@zb.ubot("extract")
async def _(c, m, _):
    # Bersihkan file lama (misal lebih dari 1 jam)
    cleanup_old_files(["downloads"], age_seconds=3600)
    # Juga cleanup extracted_* di root
    for entry in os.listdir("."):
        if entry.startswith("extracted_") and os.path.isdir(entry):
            try:
                mtime = os.path.getmtime(entry)
                if time.time() - mtime > 3600:
                    shutil.rmtree(entry)
            except Exception:
                pass

    em = Emojik(c)
    em.initialize()
    pong_, uptime_, owner_, ubot_, proses_, sukses_ = initial_ctext(c)
    pros = await m.reply(f"{em.proses} <b>Mengunduh file ...</b>")
    replied = m.reply_to_message

    password = None
    if m.command and len(m.command) > 1:
        password = ' '.join(m.command[1:]).strip()

    if not replied or not (replied.document and replied.document.mime_type in ["application/zip", "application/x-rar-compressed", "application/vnd.rar"]):
        return await pros.edit(f"{em.gagal} <b>Reply file ZIP atau RAR untuk diekstrak.</b>")

    # Simpan file di folder persistent
    download_dir = "downloads"
    os.makedirs(download_dir, exist_ok=True)
    file_name = replied.document.file_name
    download_path = os.path.join(download_dir, file_name)
    await c.download_media(replied, file_name=download_path)
    extract_dir = f"extracted_{m.id}"

    def cleanup():
        try:
            if os.path.exists(download_path):
                os.remove(download_path)
            if os.path.exists(extract_dir):
                for root, dirs, files in os.walk(extract_dir, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                os.rmdir(extract_dir)
        except Exception:
            pass

    try:
        os.makedirs(extract_dir, exist_ok=True)
        file_list = []

        try:
            if file_name.endswith(".zip"):
                with zipfile.ZipFile(download_path, 'r') as zip_ref:
                    try:
                        if password:
                            zip_ref.extractall(extract_dir, pwd=password.encode())
                        else:
                            zip_ref.extractall(extract_dir)
                        file_list = zip_ref.namelist()
                    except RuntimeError as e:
                        if "password required" in str(e).lower() or "bad password" in str(e).lower():
                            prompt = await m.reply(f"{em.gagal} <b>File ini membutuhkan password. Reply pesan ini dengan password kamu.</b>")
                            pending_extract[prompt.id] = {
                                "file_path": download_path,
                                "file_name": file_name,
                                "chat_id": m.chat.id,
                                "reply_id": m.id,
                                "extract_dir": extract_dir
                            }
                            return await pros.delete()
                        else:
                            cleanup()
                            raise
            elif file_name.endswith(".rar"):
                with rarfile.RarFile(download_path, 'r') as rar_ref:
                    try:
                        if password:
                            rar_ref.extractall(extract_dir, pwd=password)
                        else:
                            rar_ref.extractall(extract_dir)
                        file_list = rar_ref.namelist()
                    except rarfile.BadRarFile as e:
                        if "password" in str(e).lower():
                            prompt = await m.reply(f"{em.gagal} <b>File ini membutuhkan password. Reply pesan ini dengan password kamu.</b>")
                            pending_extract[prompt.id] = {
                                "file_path": download_path,
                                "file_name": file_name,
                                "chat_id": m.chat.id,
                                "reply_id": m.id,
                                "extract_dir": extract_dir
                            }
                            return await pros.delete()
                        else:
                            cleanup()
                            raise
                    except rarfile.PasswordRequired:
                        prompt = await m.reply(f"{em.gagal} <b>File ini membutuhkan password. Reply pesan ini dengan password kamu.</b>")
                        pending_extract[prompt.id] = {
                            "file_path": download_path,
                            "file_name": file_name,
                            "chat_id": m.chat.id,
                            "reply_id": m.id,
                            "extract_dir": extract_dir
                        }
                        return await pros.delete()
            else:
                cleanup()
                return await pros.edit(f"{em.gagal} <b>File tidak didukung. Hanya .zip dan .rar!</b>")

        except Exception as e:
            cleanup()
            return await pros.edit(f"{em.gagal} <b>Gagal extract: {e}</b>")

        if not file_list:
            cleanup()
            return await pros.edit(f"{em.gagal} <b>File arsip kosong atau gagal diekstrak.</b>")

        await pros.edit(f"{em.sukses} <b>Berhasil diekstrak! Mengirim file ...</b>")

        media_group = []
        count = 0
        for file in file_list:
            file_path = os.path.join(extract_dir, file)
            if os.path.isfile(file_path):
                media_group.append(InputMediaDocument(file_path))
                count += 1
                if count == 10:
                    await c.send_media_group(m.chat.id, media_group, reply_to_message_id=m.id)
                    media_group = []
                    count = 0

        if media_group:
            await c.send_media_group(m.chat.id, media_group, reply_to_message_id=m.id)

        await pros.edit(f"{em.sukses} <b>File berhasil dikirim!</b>")
        cleanup()
    except Exception:
        cleanup()

@nlx.on_message(filters.text & filters.reply, group=999)
async def handle_extract_password(c, m):
    if m.reply_to_message and m.reply_to_message.id in pending_extract:
        context = pending_extract.pop(m.reply_to_message.id)
        file_path = context["file_path"]
        file_name = context["file_name"]
        extract_dir = context["extract_dir"]
        chat_id = context["chat_id"]
        reply_id = context["reply_id"]

        password = m.text.strip()

        em = Emojik(c)
        em.initialize()
        pros = await m.reply(f"{em.proses} <b>Mencoba extract dengan password ...</b>")

        def cleanup():
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                if os.path.exists(extract_dir):
                    for root, dirs, files in os.walk(extract_dir, topdown=False):
                        for name in files:
                            os.remove(os.path.join(root, name))
                        for name in dirs:
                            os.rmdir(os.path.join(root, name))
                    os.rmdir(extract_dir)
            except Exception:
                pass

        try:
            os.makedirs(extract_dir, exist_ok=True)
            file_list = []
            if file_name.endswith(".zip"):
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    try:
                        zip_ref.extractall(extract_dir, pwd=password.encode())
                        file_list = zip_ref.namelist()
                    except RuntimeError as e:
                        cleanup()
                        return await pros.edit(f"{em.gagal} <b>Password salah atau file corrupt: {e}</b>")
            elif file_name.endswith(".rar"):
                with rarfile.RarFile(file_path, 'r') as rar_ref:
                    try:
                        rar_ref.extractall(extract_dir, pwd=password)
                        file_list = rar_ref.namelist()
                    except Exception as e:
                        cleanup()
                        return await pros.edit(f"{em.gagal} <b>Password salah atau file corrupt: {e}</b>")
            else:
                cleanup()
                return await pros.edit(f"{em.gagal} <b>File tidak didukung.</b>")

            if not file_list:
                cleanup()
                return await pros.edit(f"{em.gagal} <b>File arsip kosong atau gagal diekstrak.</b>")

            await pros.edit(f"{em.sukses} <b>Berhasil diekstrak! Mengirim file ...</b>")

            media_group = []
            count = 0
            for file in file_list:
                file_path2 = os.path.join(extract_dir, file)
                if os.path.isfile(file_path2):
                    media_group.append(InputMediaDocument(file_path2))
                    count += 1
                    if count == 10:
                        await c.send_media_group(chat_id, media_group, reply_to_message_id=reply_id)
                        media_group = []
                        count = 0

            if media_group:
                await c.send_media_group(chat_id, media_group, reply_to_message_id=reply_id)
            await pros.edit(f"{em.sukses} <b>File berhasil dikirim!</b>")
            cleanup()
        except Exception:
            cleanup()
