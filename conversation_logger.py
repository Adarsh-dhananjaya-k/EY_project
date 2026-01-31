import json
import os
from datetime import datetime

LOG_DIR = "logs"


def log_conversation(user_id, user_msg, bot_response):
    os.makedirs(LOG_DIR, exist_ok=True)
    today = datetime.now().date()
    file = f"{LOG_DIR}/log_{today}.json"

    entry = {
        "time": str(datetime.now()),
        "user_id": user_id,
        "user_message": user_msg,
        "bot_response": bot_response
    }

    data = []
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

    data.append(entry)

    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)