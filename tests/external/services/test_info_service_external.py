import pytest

from app.bot.modules.ip.childes.info.services.info import info_service
from app.bot.modules.ip.childes.info.api.info import info_api
from app.bot.modules.ip.childes.info.settings import settings
from app.bot.core.paths import bot_path


@pytest.mark.external
@pytest.mark.asyncio
async def test_info_service_success(
    session,
    fake_logging_data,
):
    ip = "23.26.71.145"

    result_info = await info_service.recieve(
        url=settings.ULR_IP_INFO.format(ip=ip, access_key=settings.ACCESS_KEY),
        path_folder_flag_country=bot_path.FLAG_DIR,
        path_folder_none_flag_img=bot_path.PATH_IMG_FLAG_NONE,
        session=session,
        logging_data=fake_logging_data,
        info_api=info_api,
    )
    assert isinstance(result_info.message, list)
    assert isinstance(result_info.message[0], str)
    assert isinstance(result_info.message[1], str)
    assert result_info.error is None
