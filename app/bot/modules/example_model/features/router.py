from aiogram import Router, F
from aiogram.types import Message


router: Router = Router(name="example_model.features")


@router.message(F.text == "example_model.features")
async def main(message: Message) -> None:
    """Router для примера"""
    await message.reply(text="helo, это features router")
