# Example 3-9. Coroutine cancellation with CancelledError
import asyncio


async def f():
    try:
        while True:
            await asyncio.sleep(0)
    # Our coroutine function now handles an exception. In fact, it handles the
    # specific exception type used throughout the asyncio library for task
    # cancellation: asyncio.CancelledError. Note that the exception is being
    # injected into the coroutine from outside; i.e., by the event loop, which
    # we’re still simulating with manual send() and throw() commands. In real
    # code, which you’ll see later, CancelledError is raised inside the
    # task-wrapped coroutine when tasks are cancelled.
    except asyncio.CancelledError:
        # A simple message to say that the task got cancelled. Note that by
        # handling the exception, we ensure it will no longer propagate and
        # our coroutine will return .
        print('I was cancelled!')
    else:
        return 111
coro = f()
coro.send(None)
coro.send(None)
# Here we throw() the CancelledError exception.
coro.throw(asyncio.CancelledError)

# After we run, we should notice:
# - As expected, we see our cancellation message being printed.
# - Our coroutine exits normally. (Recall that the StopIteration exception is
#   the normal way that coroutines exit.)
