# Example 3-8. Using coro.throw() to inject exceptions into a coroutine
import asyncio


async def f():
    await asyncio.sleep(0)
# As before, a new coroutine is created from the coroutine function f()
coro = f()
coro.send(None)
# Instead of doing another send(), we call throw() and provide an exception
# class and a value. This raises an exception inside our coroutine, at the
# await point.
coro.throw(Exception, 'blah')
