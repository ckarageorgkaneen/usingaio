# Example 3-36. The executor takes too long to finish
import time
import asyncio


async def main():
    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, blocking)
    print(f'{time.ctime()} Hello!')
    await asyncio.sleep(1.0)
    print(f'{time.ctime()} Goodbye!')


def blocking():
    # This code sample is exactly the same as the one in Example 3-3, except
    # that the sleep time in the blocking function is now longer than in the
    # async one.
    time.sleep(1.5)
    print(f"{time.ctime()} Hello from a thread!")


asyncio.run(main())
