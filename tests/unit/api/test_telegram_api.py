import pytest

from app.bot.modules.ip.childes.telegram.api.telegram import telegram_api


@pytest.mark.unit
@pytest.mark.asyncio
async def test_telegram_api_success():
    api_id = 123
    first_name = "first"
    last_name = "last"
    user_name = "user"

    result_telegram = await telegram_api.get_user_info(
        api_id=api_id,
        first_name=first_name,
        last_name=last_name,
        user_name=user_name,
    )

    assert isinstance(result_telegram.message, str)
    assert str(api_id) in result_telegram.message
    assert first_name in result_telegram.message
    assert last_name in result_telegram.message
    assert user_name in result_telegram.message
