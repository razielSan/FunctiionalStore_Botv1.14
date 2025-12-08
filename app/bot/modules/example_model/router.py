from aiogram import Router, F
from aiogram.types import Message


router: Router = Router(name="example_model")


@router.message(F.text == "example_model")
async def main(message: Message) -> None:
    """Роутер для примера"""
    await message.reply(text=f"Hi, это example_model router")
