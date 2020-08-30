# Example 4-18. The application layer: producing metrics
import argparse
import asyncio
from random import randint, uniform
from datetime import datetime as dt
from datetime import timezone as tz
from contextlib import suppress
import zmq
import zmq.asyncio
import psutil

ctx = zmq.asyncio.Context()


# This coroutine function will run as a long-lived coroutine, continually
# sending out data to the server process.
async def stats_reporter(color: str):
    p = psutil.Process()
    # Create a ØMQ socket. As you know, there are different flavors of socket;
    # this one is a PUB type, which allows one-way messages to be sent to
    # another ØMQ socket. This socket has—as the ØMQ guide says—superpowers.
    # It will automatically handle all reconnection and buffering logic for
    # us.
    sock = ctx.socket(zmq.PUB)
    sock.setsockopt(zmq.LINGER, 1)
    # Connect to the server.
    sock.connect('tcp://localhost:5555')
    # Our shutdown sequence is driven by KeyboardInterrupt, farther down. When
    # that signal is received, all the tasks will be cancelled. Here I handle
    # the raised CancelledError with the handy suppress() context manager from
    # the context lib standard library module.
    with suppress(asyncio.CancelledError):
        # Iterate forever, sending out data to the server.
        while True:
            # Since ØMQ knows how to work with complete messages, and not just
            # chunks off a bytestream, it opens the door to a bunch of useful
            # wrappers around the usual sock.send() idiom: here, I use one of
            # those helper methods, send_json(), which will automatically
            # serialize the argument into JSON. This allows us to use a dict()
            # directly.
            await sock.send_json(dict(
                color=color,
                # A reliable way to transmit datetime information is via the
                # ISO 8601 format. This is especially true if you have to pass
                # datetime data between software written in different
                # languages, since the vast majority of language
                # implementations will be able to work with this standard.
                timestamp=dt.now(tz=tz.utc).isoformat(),
                cpu=p.cpu_percent(),
                mem=p.memory_full_info().rss / 1024 / 1024
            ))
            await asyncio.sleep(1)
    # To end up here, we must have received the CancelledError exception
    # resulting from task cancellation. The ØMQ socket must be closed to allow
    # program shutdown.
    sock.close()


async def main(args):
    asyncio.create_task(stats_reporter(args.color))
    leak = []
    with suppress(asyncio.CancelledError):
        while True:
            # The main() function symbolizes the actual microservice
            # application. Fake work is produced with this sum over random
            # numbers, just to give us some nonzero data to view in the
            # visualization layer a bit later.
            sum(range(randint(1_000, 10_000_000)))
            await asyncio.sleep(uniform(0, 1))
            leak += [0] * args.leak

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # I’m going to create multiple instances of this application, so it will
    # be convenient to be able to distinguish between them (later, in the
    # graphs) with a --color parameter.
    parser.add_argument('--color', type=str)
    parser.add_argument('--leak', type=int, default=0)
    args = parser.parse_args()
    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        print('Leaving...')
        # Finally, the ØMQ context can be terminated.
        ctx.term()
