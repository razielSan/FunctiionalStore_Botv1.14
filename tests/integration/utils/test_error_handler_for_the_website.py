import pytest
from aiohttp import ClientSession
from aiohttp import request, web
import json

from app.error_handlers.network import error_handler_for_the_website


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status",
    [403, 404, 205, 216, 301, 310, 501, 513],
)
async def test_error_status_code_response(aiohttp_server, fake_logging_data, status):
    """
    Тестируем на отличные от 200 кода и 202 кода статусы.

    Работа с error_handler_for_the_website.
    """
    # Определяем какие данные будет отдавать web запрос
    async def handler(request):
        return web.Response(status=status)

    app = web.Application()  # веб приложение
    app.router.add_get("/", handler)  # url запроса
    server = await aiohttp_server(app)  # сервер для отправки запроса

    # делаем запроса
    async with ClientSession() as session:
        resp = await error_handler_for_the_website(
            session=session,
            url=str(server.make_url("/")),
            logging_data=fake_logging_data,
        )

    # Проверяем статус код и наличие ошбики
    assert resp.status == status
    assert resp.error is not None


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "content_type",
    [
        "application/json",
        "text/plain",
        "application/octet-stream",
    ],
)
async def test_response(aiohttp_server, fake_logging_data, content_type):
    """

    Работа с error_handler_for_the_website.
    """

    data_type: None = None  # тип даннхых для функции
    text: None = None  # текст для запроса

    if content_type == "text/plain":
        data_type = "TEXT"
        text = "hello World"

    if content_type == "application/json":
        data_type = "JSON"
        text = json.dumps({"value": "Hello World"})

    if content_type == "application/octet-stream":
        data_type = "BYTES"
        text = "Hello World"

    # Определяем какие данные будет отдавать web запрос
    async def handler(request):
        return web.Response(
            status=200,
            content_type=content_type,
            charset="utf-8",
            text=text,
        )

    app = web.Application()  # веб приложение
    app.router.add_get("/", handler)  # url запроса
    server = await aiohttp_server(app)  # сервер для отправки запроса

    # делаем запроса
    async with ClientSession() as session:
        resp = await error_handler_for_the_website(
            data_type=data_type,
            session=session,
            url=str(server.make_url("/")),
            logging_data=fake_logging_data,
        )
    if content_type == "application/json":
        assert isinstance(resp.message, dict)
    elif content_type == "text/plain":
        assert isinstance(resp.message, str)
    elif content_type == "application/octet-stream":
        assert isinstance(resp.message, bytes)
