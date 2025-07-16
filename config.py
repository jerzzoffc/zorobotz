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

NO_GCAST = [-1002357381726]

load_dotenv()

id_button = {}
CMD_HELP = {}


DEVS = [1448998841]

devs_boong = list(map(int, getenv("devs_boong", "").split()))
api_id = int(getenv("api_id", ""))
api_hash = getenv("api_hash", "")
bot_token = getenv("bot_token", "")
bot_id = int(getenv("bot_id", ""))
db_name = getenv("db_name", "")
log_pic = getenv("log_pic", "https://")
def_bahasa = getenv("def_bahasa", "id")
owner_id = int(getenv("owner_id", ""))
the_cegers = list(
    map(
        int,
        getenv(
            "the_cegers",
            "1448998841",
        ).split(),
    )
)
dump = int(getenv("dump", ""))
bot_username = getenv("bot_username", "")
log_userbot = int(getenv("log_userbot", ""))
log_autoreply = int(getenv("log_userbot", ""))
default_afk_log = int(getenv("log_userbot", ""))
nama_bot = getenv("nama_bot", "")
nama_ip = getenv("nama_ip", "")
gemini_api = getenv("gemini_api", "")
botcax_api = getenv("botcax_api", "moire_mor")

# === MongoDB Loyalty Point ===
from pymongo import MongoClient
mongo_url = "mongodb+srv://"
mongo_client = MongoClient(mongo_url)
mongo_db = mongo_client["ubotliteloyal"] 
mongo_points = mongo_db["loyalty_points"]

if owner_id not in the_cegers:
    the_cegers.append(owner_id)
if owner_id not in DEVS:
    DEVS.append(owner_id)
for a in the_cegers:
    DEVS.append(a)