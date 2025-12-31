import pytest

from app.bot.modules.proxies.childes.free_proxy.services.free_proxy import (
    free_proxy_service,
)
from app.bot.modules.proxies.childes.free_proxy.settings import settings


@pytest.mark.unit
@pytest.mark.parametrize("proxies", ["http", "https"])
@pytest.mark.asyncio
async def test_free_proxy_success_unit(fake_free_proxy, fake_logging_data, proxies):
    progress_call = []

    async def fake_notifier(text: str):
        progress_call.append(text)

    result = await free_proxy_service.recieve(
        type_proxy=proxies,
        list_data_proxies=settings.LIST_DATA_PROXIES,
        get_free_proxy=fake_free_proxy,
        notify_progress=fake_notifier,
        logging_data=fake_logging_data,
    )
    assert isinstance(result.message, str)
    assert result.message.count(proxies) == 8
    assert len(progress_call) > 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_free_proxy_error_unit(fake_free_proxy_error, fake_logging_data):
    progress_call = []

    async def fake_notifier(text: str):
        progress_call.append(text)

    result = await free_proxy_service.recieve(
        type_proxy="http",
        list_data_proxies=settings.LIST_DATA_PROXIES,
        get_free_proxy=fake_free_proxy_error,
        notify_progress=fake_notifier,
        logging_data=fake_logging_data,
    )
    assert result.message is None
    assert isinstance(result.error, str)
    assert result.error == "В настоящее время рабочих прокси-серверов нет.."
