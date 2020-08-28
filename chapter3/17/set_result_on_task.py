# Example 3-17. Calling set_result() on a Task
import asyncio
from contextlib import suppress


async def main(f: asyncio.Future):
    await asyncio.sleep(1)
    try:
        # A Task instance is being passed in. It satisfies the type signature
        # of the function (because Task is a subclass of Future ), but since
        # Python 3.8, we’re no longer allowed to call set_result() on a Task:
        # an attempt will raise RuntimeError. The idea is that a Task
        # represents a running coroutine, so the result should always come
        # only from that.
        f.set_result('I have finished.')
    except RuntimeError as e:
        print(f'No longer allowed: {e}')
        # We can, however, still cancel() a task, which will raise
        # CancelledError inside the underlying coroutine.
        f.cancel()
loop = asyncio.get_event_loop()
# The only difference is that we create a Task instance instead of a Future.
# Of course, the Task API requires us to provide a coroutine; we just use
# sleep() because it’s convenient.
fut = asyncio.Task(asyncio.sleep(1_000_000))
print(fut.done())
loop.create_task(main(fut))
with suppress(asyncio.CancelledError):
    loop.run_until_complete(fut)
print(fut.done())
print(fut.cancelled())
