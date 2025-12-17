from dataclasses import dataclass
from typing import Optional


@dataclass
class ModuleInfo:
    """Модель для хранения роутера и settings модуля."""
    root: Optional[str]
    router: object
    settings: object
    parent: Optional[str]
