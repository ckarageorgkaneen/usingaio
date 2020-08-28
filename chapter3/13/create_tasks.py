# Example 3-13. Creating tasks
import asyncio


async def f():
    # Create some tasks!
    loop = asyncio.get_event_loop()
    for i in range():
        loop.create_task('<some other coro>')
