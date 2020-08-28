# Example 3-7. Using await on a coroutine
import asyncio


async def f():
    await asyncio.sleep(1.0)
    return 123


async def main():
    # Calling f() produces a coroutine; this means we are allowed to await it.
    # The value of the result variable will be 123 when f() completes.
    result = await f()
    return result

asyncio.run(main())
