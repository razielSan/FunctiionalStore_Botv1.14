from pathlib import Path
import app

APP_DIR:  Path = Path(app.__file__).resolve().parent
SRC_DIR: Path = APP_DIR.parent