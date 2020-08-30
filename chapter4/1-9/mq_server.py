# Example 4-2. A 40-line prototype server
import asyncio
from asyncio import StreamReader, StreamWriter, gather
from collections import deque, defaultdict
from typing import Deque, DefaultDict
# Imports from our msgproto.py module.
from msgproto import read_msg, send_msg

# A global collection of currently active subscribers. Every time a client
# connects, they must first send a channel name they’re subscribing to. A
# deque will hold all the subscribers for a particular channel.
SUBSCRIBERS: DefaultDict[bytes, Deque] = defaultdict(deque)


async def client(reader: StreamReader, writer: StreamWriter):
    # The client() coroutine function will produce a long-lived coroutine for
    # each new connection. Think of it as a callback for the TCP server
    # started in main(). On this line, I’ve shown how the host and port of the
    # remote peer can be obtained, for example, for logging.
    peername = writer.get_extra_info('peername')
    # Our protocol for clients is the following:
    #   • On first connect, a client must send a message containing the
    #     channel to subscribe to (here, subscribe_chan).
    #   • Thereafter, for the life of the connection, a client sends a message
    #     to a channel by first sending a message containing the destination
    #     channel name, followed by a message containing the data. Our broker
    #     will send such data messages to every client subscribed to that
    #     channel name.
    subscribe_chan = await read_msg(reader)
    # Add the StreamWriter instance to the global collection of subscribers.
    SUBSCRIBERS[subscribe_chan].append(writer)
    print(f'Remote {peername} subscribed to {subscribe_chan}')
    try:
        # An infinite loop, waiting for data from this client. The first
        # message from a client must be the destination channel name.
        while channel_name := await read_msg(reader):
            # Next comes the actual data to distribute to the channel.
            data = await read_msg(reader)
            print(f'Sending to {channel_name}: {data[:19]}...')
            # Get the deque of subscribers on the target channel.
            conns = SUBSCRIBERS[channel_name]
            # Some special handling if the channel name begins with the magic
            # word /queue: in this case, we send the data to only one of the
            # subscribers, not all of them. This can be used for sharing work
            # between a bunch of workers, rather than the usual pub-sub
            # notification scheme, where all subscribers on a channel get all
            # the messages.
            if conns and channel_name.startswith(b'/queue'):
                # Here is why we use a deque and not a list: rotation of the
                # deque is how we keep track of which client is next in line
                # for /queue distribution. This seems expensive until you
                # realize that a single deque rotation is an O(1) operation.
                conns.rotate()
                # Target only whichever client is first; this changes after
                # every rotation.
                conns = [conns[0]]
            # Create a list of coroutines for sending the message to each
            # writer, and then unpack these into gather() so we can wait for
            # all of the sending to complete. This line is a bad flaw in our
            # program, but it may not be obvious why: though it may be true
            # that all of the sending to each subscriber will happen
            # concurrently, what happens if we have one very slow client? In
            # this case, the gather() will finish only when the slowest
            # subscriber has received its data. We can’t receive any more data
            # from the sending client until all these send_msg() coroutines
            # finish. This slows all message distribution to the speed of the
            # slowest subscriber.
            await gather(*[send_msg(c, data) for c in conns])
    except asyncio.CancelledError:
        print(f'Remote {peername} closing connection.')
        writer.close()
        await writer.wait_closed()
    except asyncio.IncompleteReadError:
        print(f'Remote {peername} disconnected')
    finally:
        print(f'Remote {peername} closed')
        # When leaving the client() coroutine, we make sure to remove
        # ourselves from the global SUBSCRIBERS collection. Unfortunately,
        # this is an O(n) operation, which can be a little expensive for very
        # large n. A different data structure would fix this, but for now we
        # console ourselves with the knowledge that connections are intended
        # to be long-lived—thus, there should be few disconnection events—and
        # n is unlikely to be very large (say ~10,000 as a rough
        # order-of-magnitude estimate), and this code is at least easy to
        # understand.
        SUBSCRIBERS[subscribe_chan].remove(writer)


async def main(*args, **kwargs):
    server = await asyncio.start_server(*args, **kwargs)
    async with server:
        await server.serve_forever()
try:
    asyncio.run(main(client, host='127.0.0.1', port=25000))
except KeyboardInterrupt:
    print('Bye!')
