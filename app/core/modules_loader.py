from dataclasses import dataclass
from typing import Optional


@dataclass
class ModuleInfo:
    root: Optional[str]
    router: object
    settings: object
    parent: Optional[str]
