# modules/logs.py

import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler("logs.txt", maxBytes=50_000_000, backupCount=10),
        logging.StreamHandler(),
    ],
)

# Reduce Pyrogram noise
logging.getLogger("pyrogram").setLevel(logging.WARNING)

# Keep a named logger if you ever need it
logger = logging.getLogger(__name__)

# Provide a simple alias so other modules can import `logging` directly:
# from modules.logs import logging
# and call logging.info(...), logging.error(...), etc.
# (They will use the configured root handlers above.)
