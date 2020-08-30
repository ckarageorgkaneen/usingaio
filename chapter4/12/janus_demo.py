# Example 4-12. Connecting coroutines and threads with a Janus queue
import asyncio
import random
import time
import janus


async def main():
    loop = asyncio.get_running_loop()
    # Create a Janus queue. Note that just like an asyncio.Queue, the Janus
    # queue will be associated with a specific event loop. As usual, if you
    # don’t provide the loop parameter, the standard get_event_loop() call
    # will be used internally.
    queue = janus.Queue()  # older version: janus.Queue(loop=loop)
    loop.run_in_executor(None, data_source, queue)
    # Our main() coroutine function simply waits for data on a queue. This
    # line will suspend until there is data, exactly until there is data,
    # exactly like calling get() on an asyncio.Queue instance. The queue
    # object has two faces: this one is called async_q and provides the
    # async-compatible queue API.
    while (data := await queue.async_q.get()) is not None:
        # Print a message.
        print(f'Got {data} off queue')
    print('Done.')


def data_source(queue):
    for i in range(10):
        r = random.randint(0, 4)
        # Inside the data_source() function, a random int is generated, which
        # is used both as a sleep duration and a data value. Note that the
        # time.sleep() call is blocking, so this function must be executed in
        # a thread.
        time.sleep(r)
        # Place the data onto the Janus queue. This shows the other face of
        # the Janus queue: sync_q, which provides the standard, blocking Queue
        # API.
        queue.sync_q.put(r)
    queue.sync_q.put(None)


asyncio.run(main())
