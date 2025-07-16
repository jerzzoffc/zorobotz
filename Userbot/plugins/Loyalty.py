from config import owner_id, DEVS, mongo_points, mongo_db
from Userbot.helper.loyalty import (
    add_loyalty_point,
    get_loyalty_point,
    reset_loyalty_point,
    set_loyalty_point,
)
from Userbot.helper.database import dB
from datetime import timedelta

from datetime import datetime
from dateutil.relativedelta import relativedelta
from pytz import timezone

from Userbot.helper.tools import zb
from Userbot import bot
from pyrogram.errors import FloodWait, InputUserDeactivated, PeerIdInvalid, UserIsBlocked

from Userbot.helper.broadcast_helper import broadcast_to_clients
import asyncio
from Userbot.helper.tools import Emojik, h_s, initial_ctext, get_msg_button, create_inline_keyboard
#refferal
from Userbot.helper.loyalty import regenerate_referral_code, can_generate_new_code
from Userbot.helper.loyalty import get_referral_by_code, can_generate_new_code, generate_referral_code, save_referral_code
from config import owner_id

__MODULES__ = "Loyalty"

def help_string(org):
    return h_s(org, "help_loyalty")
    
async def get_user_name(client, user_id):
    try:
        user = await client.get_users(user_id)
        return user.first_name if user.first_name else str(user_id)
    except Exception:
        return str(user_id)

def is_owner(user_id):
    return user_id == owner_id or user_id in DEVS

def get_claim_minimum():
    config = mongo_db["config"].find_one({"_id": "loyalty"})
    if config and "claim_min" in config:
        return int(config["claim_min"])
    return 3

def set_claim_minimum(val):
    mongo_db["config"].update_one({"_id": "loyalty"}, {"$set": {"claim_min": int(val)}}, upsert=True)

def add_user_claim_count(user_id, count=1):
    mongo_db["stats_claim"].update_one(
        {"user_id": user_id}, {"$inc": {"claim_count": count}}, upsert=True
    )

def get_user_claim_count(user_id):
    doc = mongo_db["stats_claim"].find_one({"user_id": user_id})
    return int(doc["claim_count"]) if doc and "claim_count" in doc else 0

# === LOGIC LOYALTY ===

async def loyalty_mypoint_logic(client, user_id, reply_func):
    points = get_loyalty_point(user_id)
    min_claim = get_claim_minimum()
    total_claim = get_user_claim_count(user_id)
    reward_avail = points // min_claim
    next_claim = min_claim - (points % min_claim)
    text = (
        f"<emoji id=5350404703823883106>⭐️</emoji> Loyalty Point Anda: <b>{points}</b>/{min_claim}\n"
        f"<emoji id=5359664288241829619>🎁</emoji> Total berhasil klaim reward: <b>{total_claim}</b> kali\n"
    )
    if reward_avail > 0:
        text += f"✅ Anda bisa claim reward sebanyak <b>{reward_avail}</b>x sekarang!\n"
    else:
        text += f"ℹ️ Kurang <b>{next_claim}</b> point lagi untuk claim berikutnya."
    await reply_func(text)

async def loyalty_claim_logic(client, user_id, reply_func):
    points = get_loyalty_point(user_id)
    min_claim = get_claim_minimum()
    reward_avail = points // min_claim
    sisa = points % min_claim
    if reward_avail == 0:
        return await reply_func(f"❌ Point Anda belum cukup untuk klaim reward. Minimal {min_claim} point.")

    exp = dB.get_expired_date(user_id)
    for _ in range(reward_avail):
        if exp is not None:
            exp = exp + timedelta(days=30)
        else:
            exp = dB.get_expired_date(user_id)
            exp = exp + timedelta(days=30) if exp else None
    if exp is not None:
        dB.set_expired_date(user_id, exp)
    set_loyalty_point(user_id, sisa)
    add_user_claim_count(user_id, reward_avail)
    total_claim = get_user_claim_count(user_id)

    nama = await get_user_name(client, user_id)
    claim_text = (
        f"🎉 Selamat! Anda berhasil klaim reward <b>{reward_avail}</b> bulan akses (point terpakai: <b>{min_claim*reward_avail}</b>). "
        f"Loyalty point Anda sekarang: <b>{sisa}</b>.\n\n"
        f"🏅 Total Anda sudah pernah klaim: <b>{total_claim}</b> kali."
    )
    notif_text = (
        f"🎉 <b>Loyalty Reward Claimed!</b>\n"
        f"User <b>{nama}</b> <code>{user_id}</code> berhasil claim reward {reward_avail}x (total claim: {total_claim}).\n"
        f"Sisa point: <b>{sisa}</b>."
    )
    await reply_func(claim_text)

    await broadcast_to_clients(client, notif_text, exclude_id=user_id)
    if user_id != owner_id:
        try:
            await client.send_message(owner_id, notif_text)
        except Exception:
            pass

async def loyalty_leaderboard_logic(client, reply_func):
    leaderboard = list(mongo_points.find().sort("points", -1).limit(10))
    if not leaderboard:
        return await reply_func("Belum ada data loyalty point.")
    min_claim = get_claim_minimum()
    msg = f"🏆 <b>Loyalty Point Leaderboard (/{min_claim})</b> 🏆\n"
    for i, doc in enumerate(leaderboard, 1):
        uid = doc["user_id"]
        pts = doc["points"]
        total_claim = get_user_claim_count(uid)
        nama = await get_user_name(client, uid)
        mention = f'<a href="tg://user?id={uid}">{nama}</a>'
        msg += f"{i}. {mention} — <b>{pts}</b> point | <b>{total_claim}</b>x claim\n"
    await reply_func(msg, disable_web_page_preview=True)

async def loyalty_leaderboardclaim_logic(client, reply_func):
    stats = list(mongo_db["stats_claim"].find().sort("claim_count", -1).limit(10))
    if not stats:
        return await reply_func("Belum ada data claim reward.")
    msg = "🏅 <b>Leaderboard Total Claim Reward</b> 🏅\n"
    for i, doc in enumerate(stats, 1):
        uid = doc["user_id"]
        claim = doc["claim_count"]
        pts = get_loyalty_point(uid)
        nama = await get_user_name(client, uid)
        mention = f'<a href="tg://user?id={uid}">{nama}</a>'
        msg += f"{i}. {mention} — <b>{claim}</b>x claim | <b>{pts}</b> point\n"
    await reply_func(msg, disable_web_page_preview=True)

async def loyalty_cekuserpoint_logic(client, user_id, reply_func):
    points = get_loyalty_point(user_id)
    total_claim = get_user_claim_count(user_id)
    min_claim = get_claim_minimum()
    nama = await get_user_name(client, user_id)
    await reply_func(
        f"User <code>{user_id}</code> <b>{nama}</b>:\n"
        f"• Loyalty Point: <b>{points}</b>/{min_claim}\n"
        f"• Total berhasil klaim reward: <b>{total_claim}</b> kali"
    )

# refferal
@zb.ubot("myreferral")
async def myreferral_handler(client, message, _):
    user_id = message.from_user.id
    active_code = None
    # Cek referral aktif
    ref = mongo_db["referrals"].find_one({"user_id": user_id}, sort=[('_id', -1)])
    if ref:
        code = ref["code"]
        used = ref.get("used", False)
        status = "✅ <b>Bisa dipakai</b>" if not used else "❌ <b>Sudah dipakai</b>"
        msg = f"""
<b>Kode Referral Kamu:</b>
<code>{code}</code>
Status: {status}
"""
        if not used:
            msg += "\nBagikan kode ini ke teman, jika dipakai kamu dapat 1 Loyalty Point!"
        else:
            msg += "\nKode referral ini sudah tidak aktif. Jika ingin kode baru, minta owner untuk regen."
        return await message.reply(msg)
    else:
        return await message.reply("Kamu belum punya kode referral. Kode referral akan dibuat otomatis saat kamu berhasil membuat ubot.")

@zb.ubot("regenreferral")
async def regen_referral_cmd(client, message, _):
    if not is_owner(message.from_user.id):
        return
    args = (message.text or "").split()
    if len(args) != 2:
        return await message.reply("Format: .regenreferral <user_id>")
    user_id = int(args[1])
    if not can_generate_new_code(user_id):
        return await message.reply("User masih punya kode referral aktif yang belum dipakai!")
    code = regenerate_referral_code(user_id, owner_id)
    await message.reply(f"Kode referral baru untuk <code>{user_id}</code>: <code>{code}</code>")

    # Autobroadcast ke semua user yang pernah /start ubot
    notif_text = (
        f"🔄 <b>Referral Regenerated</b>\n"
        f"Kode referral baru telah digenerate untuk user <code>{user_id}</code>:\n"
        f"<code>{code}</code>"
    )
    await broadcast_to_clients(client, notif_text)

@zb.ubot("regenreferralall")
async def regenreferralall_handler(client, message, _):
    if not is_owner(message.from_user.id):
        return await message.reply("Hanya owner/developer yang dapat menggunakan perintah ini.")
    # Cari semua user yang referral terakhirnya sudah terpakai, tapi tidak punya kode aktif
    pipeline = [
        {"$sort": {"_id": -1}},
        {"$group": {"_id": "$user_id", "last_ref": {"$first": "$$ROOT"}}}
    ]
    refs = list(mongo_db["referrals"].aggregate(pipeline))
    updated = []
    for user in refs:
        user_id = user["_id"]
        # skip jika masih ada kode referral aktif
        active = mongo_db["referrals"].find_one({"user_id": user_id, "used": False})
        if active:
            continue
        last_ref = user["last_ref"]
        if last_ref.get("used", False):
            code = regenerate_referral_code(user_id, owner_id)
            updated.append((user_id, code))
    if not updated:
        await message.reply("Tidak ada user yang memenuhi syarat untuk generate ulang kode referral.")
        return

    # Compose detail message
    notif_detail = "<b>Referral Baru Digenerate Global\nbagi kode referral yang audah terpakai.</b>\n\n"
    notif_detail += "\n".join([f"<code>{uid}</code> | <code>{code}</code>" for uid, code in updated])

    await message.reply(f"Berhasil generate ulang {len(updated)} kode referral:\n\n" + notif_detail)

    # Autobroadcast ke semua user yang pernah /start ubot
    broadcast_text = (
        "<b>🔄 Referral Regenerated Massal</b>\n"
        "Kode referral baru telah digenerate otomatis untuk user yang kode referralnya sudah terpakai!\n\n"
        "<b>Daftar ID User & Kode:</b>\n" +
        "\n".join([f"<code>{uid}</code> | <code>{code}</code>" for uid, code in updated])
    )
    await broadcast_to_clients(client, broadcast_text)

# === HANDLER COMMAND (tetap support .command) ===

@zb.ubot("mypoint")
async def mypoint_handler(client, message, _):
    await loyalty_mypoint_logic(client, message.from_user.id, message.reply)

@zb.ubot("claim")
async def claim_handler(client, message, _):
    await loyalty_claim_logic(client, message.from_user.id, message.reply)

@zb.ubot("leaderboard")
async def leaderboard_handler(client, message, _):
    await loyalty_leaderboard_logic(client, lambda t, **kw: message.reply(t, **kw))

@zb.ubot("leaderboardclaim")
async def leaderboard_claim_handler(client, message, _):
    await loyalty_leaderboardclaim_logic(client, lambda t, **kw: message.reply(t, **kw))

@zb.ubot("cekpoint")
async def cekuserpoint_handler(client, message, _):
    if not is_owner(message.from_user.id):
        return
    args = (message.text or "").split()
    if len(args) != 2:
        return await message.reply("Format salah. Gunakan: .cekuserpoint <user_id>")
    try:
        user_id = int(args[1])
    except Exception:
        return await message.reply("Format salah. Gunakan: .cekuserpoint <user_id>")
    await loyalty_cekuserpoint_logic(client, user_id, message.reply)

# -- Handler admin lain/owner tetap seperti sebelumnya --
@zb.ubot("addpoint")
async def addpoint_handler(client, message, _):
    if not is_owner(message.from_user.id):
        return
    args = (message.text or "").split()
    if len(args) != 3:
        return await message.reply("Format salah. Gunakan: .addpoint <user_id> <jumlah>")
    try:
        user_id = int(args[1])
        jumlah = int(args[2])
    except Exception:
        return await message.reply("Format salah. Gunakan: .addpoint <user_id> <jumlah>")
    points = get_loyalty_point(user_id) + jumlah
    set_loyalty_point(user_id, points)
    await message.reply(f"✅ Berhasil menambah {jumlah} point untuk <code>{user_id}</code>. Sekarang: {points} point.")
    nama = await get_user_name(client, user_id)
    notif_text = (
        f"➕ <b>Loyalty Point Manual</b>\n"
        f"User <b>{nama}</b> <code>{user_id}</code> mendapatkan tambahan <b>{jumlah}</b> point dari Owner/Admin.\n"
        f"Total point saat ini: <b>{points}</b>."
    )
    await broadcast_to_clients(client, notif_text, exclude_id=user_id)

@zb.ubot("delpoint")
async def delpoint_handler(client, message, _):
    if not is_owner(message.from_user.id):
        return
    args = (message.text or "").split()
    if len(args) != 3:
        return await message.reply("Format salah. Gunakan: .delpoint <user_id> <jumlah>")
    try:
        user_id = int(args[1])
        jumlah = int(args[2])
    except Exception:
        return await message.reply("Format salah. Gunakan: .delpoint <user_id> <jumlah>")
    points = max(0, get_loyalty_point(user_id) - jumlah)
    set_loyalty_point(user_id, points)
    await message.reply(f"✅ Berhasil mengurangi {jumlah} point untuk <code>{user_id}</code>. Sekarang: {points} point.")

@zb.ubot("renew")
async def renew_handler(client, message, _):
    if not is_owner(message.from_user.id):
        return
    args = (message.text or "").split()
    if len(args) != 2:
        return await message.reply("Format salah. Gunakan: .renew <user_id>")
    try:
        user_id = int(args[1])
    except Exception:
        return await message.reply("Format salah. Gunakan: .renew <user_id>")
    exp = dB.get_expired_date(user_id)
    if exp is not None:
        new_exp = exp + timedelta(days=30)
        dB.set_expired_date(user_id, new_exp)
    points = add_loyalty_point(user_id)
    await message.reply(f"✅ Masa sewa <code>{user_id}</code> ditambah 1 bulan & point loyalty sekarang: {points}")
    nama = await get_user_name(client, user_id)
    notif_text = (
        f"🔄 <b>Perpanjangan Sewa Manual</b>\n"
        f"User <b>{nama}</b> <code>{user_id}</code> masa aktifnya diperpanjang 1 bulan oleh Owner/Admin & mendapat 1 loyalty point.\n"
        f"Total loyalty point sekarang: <b>{points}</b>."
    )
    await broadcast_to_clients(client, notif_text, exclude_id=user_id)

@zb.ubot("setclaim")
async def setclaim_handler(client, message, _):
    if not is_owner(message.from_user.id):
        return
    args = (message.text or "").split()
    if len(args) != 2:
        return await message.reply("Format salah. Gunakan: .setclaim <jumlah_point>")
    try:
        jumlah = int(args[1])
        if jumlah < 1 or jumlah > 100:
            return await message.reply("Batas minimal 1, maksimal 100.")
    except Exception:
        return await message.reply("Format salah. Gunakan: .setclaim <jumlah_point>")
    set_claim_minimum(jumlah)
    await message.reply(f"✅ Minimal point claim reward diubah menjadi <b>{jumlah}</b> point.")


#@zb.ubot("help loyalty")
#async def loyalty_help_handler(client, message, _):
#    help_text = (
#        "<b>Daftar Perintah Loyalty Point:</b>\n"
#        "<code>.mypoint</code> — Cek point dan total claim Anda\n"
#        "<code>.claim</code> — Klaim reward jika point cukup (otomatis multi-claim jika point banyak)\n"
#        "<code>.leaderboard</code> — Top 10 loyalty point tertinggi\n"
#        "<code>.leaderboardclaim</code> — Top 10 total claim reward\n"
#        "<code>.cekuserpoint &lt;user_id&gt;</code> — [Owner] Cek point & claim user\n"
#        "<code>.addpoint &lt;user_id&gt; &lt;jumlah&gt;</code> — [Owner] Tambah point user\n"
#        "<code>.delpoint &lt;user_id&gt; &lt;jumlah&gt;</code> — [Owner] Kurangi point user\n"
#        "<code>.setclaim &lt;jumlah_point&gt;</code> — [Owner] Set minimum point claim\n"
#        "<code>.renew &lt;user_id&gt;</code> — [Owner] Tambah masa sewa user 1 bulan & +1 point loyalty\n"
#    )
#    await message.reply(help_text)
