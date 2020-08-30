# Example 4-13. Minimal aiohttp example
from aiohttp import web


async def hello(request):
    return web.Response(text="Hello, world")
# An Application instance is created.
app = web.Application()
# A route is created, with the target coroutine hello() given as the handler.
app.router.add_get('/', hello)
# The web application is run.
web.run_app(app, port=8080)
