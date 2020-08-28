# Example 3-29. Destroyer of pending tasks
import asyncio


async def f(delay):
    await asyncio.sleep(delay)
loop = asyncio.get_event_loop()
# Task 1 will run for 1 second.
t1 = loop.create_task(f(1))
# Task 2 will run for 2 seconds.
t2 = loop.create_task(f(2))
# Run only until task 1 is complete.
loop.run_until_complete(t1)
loop.close()
