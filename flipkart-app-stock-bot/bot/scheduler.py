import random
import time


def sleep_random(min_minutes=8, max_minutes=15):
    seconds = random.randint(min_minutes * 60, max_minutes * 60)
    print(f"⏰ Sleeping {seconds//60} minutes...")
    time.sleep(seconds)
