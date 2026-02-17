import json
import os
import time

STATE_FILE = "state.json"


def load_state():
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        return json.load(open(STATE_FILE, "r", encoding="utf-8"))
    except:
        return {}


def save_state(state):
    json.dump(state, open(STATE_FILE, "w", encoding="utf-8"), indent=2)


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
