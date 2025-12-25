from pathlib import Path
from importlib import import_module

from aiogram import Router, Dispatcher
    
from app.bot.core.init_logging import bot_info_logger, bot_warning_logger  
    
    
router: Router = Router(name='youtube.childes.search')

# Register router

def register(
    dp: Dispatcher,
    parent_router: bool,
    root_router: object,
) -> None:
    if not parent_router:  # если роутер корневой
        # Проверка на то что этот роутер ни к кому не подключен
        if getattr(router, "parent_router", None) is None:
            dp.include_router(router)
            bot_info_logger.info(
                "\n[Auto] Root router inculde into dp: {}".format(router)
            )
        else:
            bot_warning_logger.warning(
                "\n[Auto] Root router already attached: {}".format(router)
            )

    else:
        if getattr(router, "parent_router", None) is None:
            root_router.include_router(router)
            bot_info_logger.info(
                "\n[Auto] Child router inculded into {}: {}".format(root_router, router)
            )
        else:
            bot_warning_logger.warning(
                "\n[Auto] Child router already attached: {}".format(router)
            )
            
# Include sub router            
current_dir = Path(__file__).resolve().parent
handlers_path = current_dir / "handlers"
            
for file in handlers_path.glob("*.py"):
    if file.name == "__init__.py":
        continue

    module_name = f"{__package__}.handlers.{file.stem}"
    module = import_module(module_name)

    handler_router = getattr(module, "router", None)

    if handler_router:
        router.include_router(handler_router)
        bot_info_logger.info(
            "\n[Auto] Sub router inculde into {}: {}".format(router, handler_router)
        )  
    