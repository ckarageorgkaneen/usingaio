# Example 3-30. Asyncio application life cycle (based on the TCP echo server
# in the Python documentation)
import asyncio
from asyncio import StreamReader, StreamWriter


# This echo() coroutine function will be used (by the server) to create a
# coroutine for each connection made. The function is using the streams API
# for networking with asyncio .
async def echo(reader: StreamReader, writer: StreamWriter):
    print('New connection.')
    try:
        # To keep the connection alive, we’ll have an infinite loop to wait
        # for messages.
        while data := await reader.readline():
            # Return the data back to the sender, but in ALL CAPS.
            writer.write(data.upper())
            await writer.drain()
        print('Leaving Connection.')
    except asyncio.CancelledError:
        # If this task is cancelled, we’ll print a message.
        print('Connection dropped!')


async def main(host='127.0.0.1', port=8888):
    # This code for starting a TCP server is taken directly from the
    # Python 3.8 documentation.
    server = await asyncio.start_server(echo, host, port)
    async with server:
        await server.serve_forever()
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('Bye!')
