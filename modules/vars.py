# Add your details here and then deploy by clicking on HEROKU Deploy button
import os
from os import environ

def _to_int(val, default=None):
    try:
        return int(str(val).strip())
    except Exception:
        return default

def _to_int_list(val, default_ids=None):
    s = os.environ.get(val, "")
    if not s:
        return list(default_ids or [])
    out = []
    for token in s.split(","):
        token = token.strip()
        if not token:
            continue
        try:
            out.append(int(token))
        except Exception:
            continue
    return out

API_ID = _to_int(environ.get("API_ID", ""), None)
API_HASH = environ.get("API_HASH", "")
BOT_TOKEN = environ.get("BOT_TOKEN", "")

OWNER = _to_int(environ.get("OWNER", ""), None)
CREDIT = environ.get("CREDIT", "SAINI BOTS")
cookies_file_path = os.getenv("cookies_file_path", "youtube_cookies.txt")

TOTAL_USERS = _to_int_list("TOTAL_USERS", default_ids=[])
AUTH_USERS = _to_int_list("AUTH_USERS", default_ids=[])
if OWNER and OWNER not in AUTH_USERS:
    AUTH_USERS.append(OWNER)

# External API (if still used elsewhere)
api_url = environ.get("API_URL", "http://master-api-v3.vercel.app/")
api_token = environ.get("API_TOKEN", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNzkxOTMzNDE5NSIsInRnX3VzZXJuYW1lIjoi4p61IFtvZmZsaW5lXSIsImlhdCI6MTczODY5MjA3N30.SXzZ1MZcvMp5sGESj0hBKSghhxJ3k1GTWoBUbivUe1I")

# NEW: Mongo + channel config for range uploader
MONGO_URI = environ.get("MONGO_URI", "")
# TXT source channel that stores .txt documents (use int ID like -100xxxxxxxxxx)
TXT_SOURCE_CHANNEL = _to_int(environ.get("TXT_SOURCE_CHANNEL", ""), None)
# Upload destination channel (use int ID like -100xxxxxxxxxx)
UPLOAD_DEST = _to_int(environ.get("UPLOAD_DEST", ""), None)

# Validate critical fields early
REQUIRED_VARS = {
    "API_ID": API_ID,
    "API_HASH": API_HASH,
    "BOT_TOKEN": BOT_TOKEN,
    "OWNER": OWNER,
}
for k, v in REQUIRED_VARS.items():
    if v in (None, "", 0):
        print(f"[vars.py] Warning: {k} is not set properly.")

if not MONGO_URI:
    print("[vars.py] Warning: MONGO_URI is empty; range uploader will be disabled until provided.")

if TXT_SOURCE_CHANNEL is None:
    print("[vars.py] Warning: TXT_SOURCE_CHANNEL is not set; provide source store channel id.")

if UPLOAD_DEST is None:
    print("[vars.py] Warning: UPLOAD_DEST is not set; provide upload destination channel id.")

  
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
api_url = "http://master-api-v3.vercel.app/"
api_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNzkxOTMzNDE5NSIsInRnX3VzZXJuYW1lIjoi4p61IFtvZmZsaW5lXSIsImlhdCI6MTczODY5MjA3N30.SXzZ1MZcvMp5sGESj0hBKSghhxJ3k1GTWoBUbivUe1I"
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.


