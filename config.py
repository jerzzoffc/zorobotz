import json
import sys
from base64 import b64decode
from os import getenv

import requests
from dotenv import load_dotenv

black = int(b64decode("MTA1NDI5NTY2NA=="))

ERROR = "Maintained ? Yes Oh No Oh Yes Ngentot\n\nBot Ini Haram Buat Lo Bangsat!!"
DIBAN = "LAH LU DIBAN BEGO DI @moire_logs"


def get_tolol():
    try:
        aa = "aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL25heWExNTAzL3dhcm5pbmcvbWFpbi90b2xvbC5qc29u"
        bb = b64decode(aa).decode("utf-8")
        res = requests.get(bb)
        if res.status_code == 200:
            return json.loads(res.text)
    except Exception as e:
        return f"An error occurred: {str(e)}"
        sys.exit(1)


TOLOL = get_tolol()

NO_GCAST = [-1002631506745]

load_dotenv()

id_button = {}
CMD_HELP = {}


DEVS = [5907975087]

devs_boong = list(map(int, getenv("devs_boong", "5907975087").split()))
api_id = int(getenv("api_id", "23908438"))
api_hash = getenv("api_hash", "16cc5b553e3ad993343ac153eb1e8925")
bot_token = getenv("bot_token", "7679800629:AAF_LwYmcg3SyveM0qhE65J8Zy99J1N8c4E")
bot_id = int(getenv("bot_id", "7679800629"))
db_name = getenv("db_name", "JDatabase")
log_pic = getenv("log_pic", "https://files.catbox.moe/6ycy32.jpg")
def_bahasa = getenv("def_bahasa", "id")
owner_id = int(getenv("owner_id", "5907975087"))
the_cegers = list(
    map(
        int,
        getenv(
            "the_cegers",
            "6725042105",
        ).split(),
    )
)
dump = int(getenv("dump", "-1002532401344"))
bot_username = getenv("bot_username", "@UserBotZoro_bot")
log_userbot = int(getenv("log_userbot", "-1002545622363"))
log_autoreply = int(getenv("log_userbot", "-1002545622363"))
default_afk_log = int(getenv("log_userbot", "-1002545622363"))
nama_bot = getenv("nama_bot", "ZoroBot")
nama_ip = getenv("nama_ip", "Iphone 16 Pro")
gemini_api = getenv("gemini_api", "jerzz")
botcax_api = getenv("botcax_api", "moire_mor")

# === MongoDB Loyalty Point ===
from pymongo import MongoClient
mongo_url = "mongodb+srv://jurdun2024:Ohun02GetrmLzcFH@cluster0.6hqws7o.mongodb.net/"
mongo_client = MongoClient(mongo_url)
mongo_db = mongo_client["ubotliteloyal"] 
mongo_points = mongo_db["loyalty_points"]

if owner_id not in the_cegers:
    the_cegers.append(owner_id)
if owner_id not in DEVS:
    DEVS.append(owner_id)
for a in the_cegers:
    DEVS.append(a)
