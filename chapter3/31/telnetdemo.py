# Example 3-31. Creating a task inside a cancellation handler
import asyncio
from asyncio import StreamReader, StreamWriter


# Pretend that this coroutine actually contacts an external server to submit
# event notifications.
async def send_event(msg: str):
    await asyncio.sleep(1)


async def echo(reader: StreamReader, writer: StreamWriter):
    print('New connection.')
    try:
        while (data := await reader.readline()):
            writer.write(data.upper())
            await writer.drain()
        print('Leaving Connection.')
    except asyncio.CancelledError:
        msg = 'Connection dropped!'
        print(msg)
        # Because the event notifier involves network access, it is common for
        # such calls to be made in a separate async task; that’s why we’re
        # using the create_task() function here.
        asyncio.create_task(send_event(msg))


async def main(host='127.0.0.1', port=8888):
    server = await asyncio.start_server(echo, host, port)
    async with server:
        await server.serve_forever()
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('Bye!')
