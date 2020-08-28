# Example 3-28. Putting it all together
import asyncio


# A simple coroutine function: sleep for a bit; then return the parameter plus
# 100.
async def f(x):
    await asyncio.sleep(0.1)
    return x + 100


# This is an async generator, which we will call inside an async list
# comprehension a bit farther down, using async for to drive the iteration.
async def factory(n):
    for x in range(n):
        await asyncio.sleep(0.1)
        # The async generator will yield a tuple of f and the iteration var x.
        # The f return value is a coroutine function, not yet a coroutine.
        yield f, x


async def main():
    # Finally, the async comprehension. This example has been contrived to
    # demonstrate a comprehension that includes both async for and await.
    # Let’s break down what’s happening inside the comprehension. First, the
    # factory(3) call returns an async generator, which must be driven by
    # iteration. Because it’s an async generator, you can’t just use for;
    # you must use async for.
    results = [await f(x) async for f, x in factory(3)]
    print('results = ', results)
asyncio.run(main())
