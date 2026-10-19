import json
import os
import time

from config import COMMANDS_FILE, CRINGE_FILE, TIMEOUT


def write_json(path, data):
    text = json.dumps(data, indent=4)
    # Write to a temp file first so a crash mid-write can't corrupt the real file
    tmp_path = path + ".tmp"
    with open(tmp_path, "w") as f:
        f.write(text)
    try:
        os.replace(tmp_path, path)
    except OSError:
        # Replacing fails if Docker mounts this single file, so fall back to writing it in place
        os.remove(tmp_path)
        with open(path, "w") as f:
            f.write(text)


def load_commands():
    if os.path.exists(COMMANDS_FILE):
        with open(COMMANDS_FILE, "r") as f:
            return json.load(f)
    write_json(COMMANDS_FILE, {})
    return {}


def save_commands():
    write_json(COMMANDS_FILE, custom_commands)


# cringe_list maps user ID -> {"expires_at": unix timestamp, "channel_id": channel to announce expiry in}
def load_cringe_list():
    if not os.path.exists(CRINGE_FILE):
        write_json(CRINGE_FILE, {})
        return {}
    with open(CRINGE_FILE, "r") as f:
        data = json.load(f)
    if isinstance(data, list):
        expires_at = time.time() + TIMEOUT
        return {user_id: {"expires_at": expires_at, "channel_id": None} for user_id in data}
    # JSON keys are always strings, so convert them back to int user IDs
    return {int(user_id): entry for user_id, entry in data.items()}


def save_cringe_list():
    write_json(CRINGE_FILE, cringe_list)


custom_commands = load_commands()
cringe_list = load_cringe_list()
