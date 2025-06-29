#🇳‌🇮‌🇰‌🇭‌🇮‌🇱‌
# Add your details here and then deploy by clicking on HEROKU Deploy button
import os
from os import environ

API_ID = int(environ.get("API_ID", "25570420"))
API_HASH = environ.get("API_HASH", "6591643fa39b5b9d0eb78cb24db17f69")
BOT_TOKEN = environ.get("BOT_TOKEN", "8134792230:AAGUCUVMS-15GCbSHeU_EE-MI0ugG6cMXxY")
OWNER = int(environ.get("OWNER", "7552584508"))
CREDIT = "𝙎𝘼𝙄𝙉𝙄 𝘽𝙊𝙏𝙎"
AUTH_USER = os.environ.get('AUTH_USERS', '7552584508').split(',')
AUTH_USERS = [int(user_id) for user_id in AUTH_USER]
if int(OWNER) not in AUTH_USERS:
    AUTH_USERS.append(int(OWNER))
  
#WEBHOOK = True  # Don't change this
#PORT = int(os.environ.get("PORT", 8080))  # Default to 8000 if not set
