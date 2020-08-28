# Example 3-10. For educational purposes only—don’t do this!
import asyncio


async def f():
    try:
        while True:
            await asyncio.sleep(0)
    except asyncio.CancelledError:
        print('Nope!')
        # Instead of printing a message, what happens if after cancellation,
        # we just go right back to awaiting another awaitable?
        while True:
            await asyncio.sleep(0)
    else:
        return 111
coro = f()
coro.send(None)
# Unsurprisingly, our outer coroutine continues to live, and it immediately
# suspends again inside the new coroutine.
coro.throw(asyncio.CancelledError)
# Everything proceeds normally, and our coroutine continues to suspend and
# resume as expected.
coro.send(None)
