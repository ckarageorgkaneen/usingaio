# Example 4-17. Clean separation with asyncio
import asyncio
import zmq
from zmq.asyncio import Context

context = Context()


async def do_receiver():
    # This code sample does the same as Example 4-15, except that now we’re
    # taking advantage of coroutines to restructure everything. Now we can
    # deal with each socket in isolation. I’ve created two coroutine
    # functions, one for each socket; this one is for the PULL socket.
    receiver = context.socket(zmq.PULL)
    receiver.connect("tcp://localhost:5557")
    # I’m using the asyncio support in pyzmq, which means that all send() and
    # recv() calls must use the await keyword. The Poller no longer appears
    # anywhere, because it’s been integrated into the asyncio event loop
    # itself.
    while message := await receiver.recv_json():
        print(f'Via PULL: {message}')


async def do_subscriber():
    # This is the handler for the SUB socket. The structure is very similar to
    # the PULL socket’s handler, but that need not have been the case. If more
    # complex logic had been required, I’d have been able to easily add it
    # here, fully encapsulated within the SUB -handler code only.
    subscriber = context.socket(zmq.SUB)
    subscriber.connect("tcp://localhost:5556")
    subscriber.setsockopt_string(zmq.SUBSCRIBE, '')
    # Again, the asyncio-compatible sockets require the await keyword to send
    # and receive.
    while message := await subscriber.recv_json():
        print(f'Via SUB: {message}')


async def main():
    await asyncio.gather(
        do_receiver(),
        do_subscriber(),
    )
asyncio.run(main())
