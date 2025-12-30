from pathlib import Path


class BotPath:
    BOT_DIR: Path = Path(__file__).resolve().parent.parent
    STATIC_DIR: Path = BOT_DIR / "static"
    FLAG_DIR: Path = STATIC_DIR / "img" / "flag"
    PATH_IMG_FLAG_NONE: Path = FLAG_DIR / "none.png"


bot_path = BotPath()
