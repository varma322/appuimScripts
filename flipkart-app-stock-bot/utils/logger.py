import logging
import os

LOG_FILE = os.path.join("logs", "app.log")
os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("flipkart_app_bot")
logger.setLevel(logging.INFO)

_fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

# file
_fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
_fh.setFormatter(_fmt)
logger.addHandler(_fh)

# console
_ch = logging.StreamHandler()
_ch.setFormatter(_fmt)
logger.addHandler(_ch)
