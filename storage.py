import json
import os

from config import COMMANDS_FILE, CRINGE_FILE


def load_commands():
    if os.path.exists(COMMANDS_FILE):
        with open(COMMANDS_FILE, "r") as f:
            return json.load(f)
    with open(COMMANDS_FILE, "w") as f:
        json.dump({}, f)
    return {}


def save_commands():
    with open(COMMANDS_FILE, "w") as f:
        json.dump(custom_commands, f, indent=4)


def load_cringe_list():
    if os.path.exists(CRINGE_FILE):
        with open(CRINGE_FILE, "r") as f:
            return json.load(f)
    with open(CRINGE_FILE, "w") as f:
        json.dump([], f)
    return []


def save_cringe_list():
    with open(CRINGE_FILE, "w") as f:
        json.dump(cringe_list, f, indent=4)


custom_commands = load_commands()
cringe_list = load_cringe_list()
