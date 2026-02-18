import json
import os
import time
import tempfile

STATE_FILE = "state.json"


def load_state():
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(state):
    """Atomic write: write to temp file first, then rename over the target."""
    tmp_fd, tmp_path = tempfile.mkstemp(dir=".", suffix=".tmp")
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        os.replace(tmp_path, STATE_FILE)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def update_product_state(url: str, status: str, price: int | None):
    """
    status: IN_STOCK / OUT_OF_STOCK / NOT_DELIVERABLE / UNKNOWN
    """
    state = load_state()

    if url not in state:
        state[url] = {
            "last_status": None,
            "last_price": None,
            "last_alert": 0
        }

    prev = state[url].copy()

    state[url]["last_status"] = status
    state[url]["last_price"] = price

    save_state(state)
    return prev, state[url]


def mark_alerted(url: str):
    state = load_state()
    if url not in state:
        state[url] = {}
    state[url]["last_alert"] = int(time.time())
    save_state(state)
