import pytest
from aiohttp import ClientSession
from aiohttp import request, web

from app.error_handlers.network import error_handler_for_the_website


@pytest.mark.asyncio
@pytest.mark.parametrize("status_codes", [["403", "404", "205", "301", "501"]])
async def test_error_status_code_response(
    aiohttp_server, fake_logging_data, status_codes
):
    pass

    for status in status_codes:

        async def handler(request):
            return web.Response(status=int(status))

        app = web.Application()
        app.router.add_get("/", handler)
        server = await aiohttp_server(app)

        async with ClientSession() as session:
            resp = await error_handler_for_the_website(
                session=session,
                url=str(server.make_url("/")),
                logging_data=fake_logging_data,
            )

        assert resp.status == int(status)
        assert resp.error is not None
