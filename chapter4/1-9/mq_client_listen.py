# Example 4-3. Listener: a toolkit for listening for messages on our message
# broker
import asyncio
import argparse
import uuid
from msgproto import read_msg, send_msg


async def main(args):
    # The uuid standard library module is a convenient way of creating an
    # “identity” for this listener. If you start up multiple instances, each
    # will have its own identity, and you’ll be able to track what is
    # happening in the logs.
    me = uuid.uuid4().hex[:8]
    print(f'Starting up {me}')
    # Open a connection to the server.
    reader, writer = await asyncio.open_connection(
        args.host, args.port)
    print(f'I am {writer.get_extra_info("sockname")}')
    # The channel to subscribe to is an input parameter, captured in
    # args.listen. Encode it into bytes before sending.
    channel = args.listen.encode()
    # By our protocol rules (as discussed in the broker code analysis
    # previously), the first thing to do after connecting is to send the
    # channel name to subscribe to.
    await send_msg(writer, channel)
    try:
        # This loop does nothing else but wait for data to appear on the
        # socket.
        while data := await read_msg(reader):
            print(f'Received by {me}: {data[:20]}')
        print('Connection ended.')
    except asyncio.IncompleteReadError:
        print('Server closed.')
    finally:
        writer.close()
        await writer.wait_closed()

if __name__ == '__main__':
    # The command-line arguments for this program make it easy to point to a
    # host, a port, and a channel name to listen to.
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', default=25000)
    parser.add_argument('--listen', default='/topic/foo')
    try:
        asyncio.run(main(parser.parse_args()))
    except KeyboardInterrupt:
        print('Bye!')
