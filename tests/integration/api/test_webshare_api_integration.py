import pytest

from app.core.response import NetworkResponseData
from app.bot.modules.proxies.childes.webshare.api.webshare import webshare_api


@pytest.mark.integration
@pytest.mark.asyncio
async def test_webshare_api_error_on_token(
    monkeypatch,
    fake_logging_data,
    session,
):
    async def fake_error_handlers(*args, **kwargs):
        return NetworkResponseData(
            error="network error", status=0, method="GET", url="test"
        )

    monkeypatch.setattr(
        "app.bot.modules.proxies.childes.webshare.api.webshare.error_handler_for_the_website",
        fake_error_handlers,
    )  # подменяем error_handler_for_the_website на fake_error_handlers

    result_webshare = await webshare_api.get_proxies(
        url_config="test",
        url_proxeis_list="test",
        api_key="test",
        session=session,
        logging_data=fake_logging_data,
    )

    assert result_webshare.error == "network error"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_webshare_api_proxy_address_error(
    monkeypatch,
    fake_logging_data,
    session,
):
    count = 0

    # Подменяем данные выдываемые error_handler_for_the_website для двух вызовов
    async def fake_error_handlers(*args, **kwargs):
        nonlocal count
        count += 1
        if count == 1:
            return NetworkResponseData(
                message={"proxy_list_download_token": "test"},
                status=200,
                method="GET",
                url="test",
            )
        return NetworkResponseData(error="proxy_address_error", status=0)

    monkeypatch.setattr(
        "app.bot.modules.proxies.childes.webshare.api.webshare.error_handler_for_the_website",
        fake_error_handlers,
    )  # подменяем error_handler_for_the_website на fake_error_handlers

    result_webshare = await webshare_api.get_proxies(
        url_config="test",
        url_proxeis_list="test",
        api_key="test",
        session=session,
        logging_data=fake_logging_data,
    )

    assert result_webshare.error == "proxy_address_error"
