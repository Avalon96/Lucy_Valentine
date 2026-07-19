import os

from dotenv import load_dotenv

OVERLORD_ROLE = "The Island Owner"
ALLOWED_ROLES = ("The Island Owner", "Uma Musume Vice Pope")

RESERVED_COMMANDS = {
    "cmd",
    "batch",
    "del",
    "batchdel",
    "allcmd",
    "export",
    "import",
    "cringe",
    "uncringe",
    "allcringe",
}

COMMANDS_FILE = "custom_commands.json"
CRINGE_FILE = "cringe_list.json"

load_dotenv()  
BOT_NAME = os.getenv("BOT_NAME", "Lucy")
CONFIG = {
    "Lucy": {
        "COMMAND_PREFIX": "!",
        "BOT_PAT": "<a:LucyPat:1521201578474737754>",
    },
    "ATRI": {
        "COMMAND_PREFIX": ".",
        "BOT_PAT": "<a:AtriPat:1521201668258267326>",
    }
}
bot = CONFIG.get(BOT_NAME, CONFIG["Lucy"])
COMMAND_PREFIX = bot["COMMAND_PREFIX"]
BOT_PAT = bot["BOT_PAT"]

HEART = "❤️"
DISGUST_MELU = "<:MelusineDisgust:1521196798046109769>"
SORA_UNAMUSED = "<a:SoraUnamused:1521201633961181405>"
ARTORIA_SLEEP = "<:ArtoriaSleep:1521217714457415802>"
AKIHA_DUMBFOUNDED = "<:AkihaDumbfounded:1521196115452493895>"
SORA_HEADSHOT = "<a:SoraHeadshot:1521201624956014793>"
SORA_SLAP = "<a:SoraSlap:1521201632044384489>"
CLUELESS = "<:clueless:1521253710460616936>"
CRINGE_REACTION_EMOJIS = (
    DISGUST_MELU,
    SORA_UNAMUSED,
    ARTORIA_SLEEP,
    AKIHA_DUMBFOUNDED,
    SORA_HEADSHOT,
    SORA_SLAP,
    CLUELESS,
)

EXPORT_CHANNEL_ID = 1521643823644803234
OVERLORD_ID = 186703004605480960
TIMEOUT = 900
