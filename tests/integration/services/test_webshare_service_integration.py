import pytest

from app.bot.modules.proxies.childes.webshare.services.webshare import webshare_service
from app.bot.modules.proxies.childes.webshare.api.webshare import webshare_api
from app.bot.modules.proxies.childes.webshare.settings import settings
from app.core.response import NetworkResponseData


@pytest.mark.integration
@pytest.mark.asyncio
async def test_webshare_service_success(fake_logging_data, session):
    class FakeApi:
        async def get_proxies(
            self,
            *args,
            **kwargs,
        ):
            return NetworkResponseData(message="proxy1\proxy2", status=200)

    webshare_result = await webshare_service.recieve(
        api_key=settings.ApiKey,
        url_config=settings.URL_CONFIG,
        url_proxies_list=settings.URL_PROXIES_LIST,
        logging_data=fake_logging_data,
        session=session,
        webshare_api=FakeApi(),
    )
    assert webshare_result.error is None
    assert isinstance(webshare_result.message, str)
