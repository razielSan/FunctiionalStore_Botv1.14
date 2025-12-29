import pytest

from app.bot.modules.password.services.password import password_service
from app.bot.modules.password.settings import settings
from app.core.tests.response import PasswordTest


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "password",
    [
        PasswordTest(
            type_passwrod=settings.SIMPLE,
            step=1,
            count_password=5,
            len_password=3,
        ),
        PasswordTest(
            type_passwrod=settings.SIMPLE,
            step=2,
            count_password=10,
            len_password=6,
        ),
        PasswordTest(
            type_passwrod=settings.SIMPLE,
            step=3,
            count_password=15,
            len_password=9,
        ),
        PasswordTest(
            type_passwrod=settings.SIMPLE,
            step=4,
            count_password=20,
            len_password=12,
        ),
        PasswordTest(
            type_passwrod=settings.DIFFICULT,
            step=1,
            count_password=25,
            len_password=6,
        ),
        PasswordTest(
            type_passwrod=settings.DIFFICULT,
            step=2,
            count_password=30,
            len_password=12,
        ),
        PasswordTest(
            type_passwrod=settings.DIFFICULT,
            step=3,
            count_password=1,
            len_password=18,
        ),
        PasswordTest(
            type_passwrod=settings.DIFFICULT,
            step=4,
            count_password=2,
            len_password=24,
        ),
    ],
)
async def test_password_service_success(
    password,
    fake_logging_data,
):

    result_password = await password_service.receive(
        type_password=password.type_passwrod,
        step=password.step,
        logging_data=fake_logging_data,
        count_password=password.count_password,
    )
    assert isinstance(result_password.message, str)

    array = result_password.message.split("\n")
    assert len(array) == password.count_password
    for psw in array:
        assert len(psw) == password.len_password
