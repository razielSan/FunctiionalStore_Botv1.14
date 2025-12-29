from typing import Awaitable, Callable

ProgressNotifier = Callable[[str], Awaitable[None]]
