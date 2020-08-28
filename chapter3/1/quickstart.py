# Example 3-1. The “Hello World” of Asyncio
import asyncio
import time


async def main():
    print(f'{time.ctime()} Hello!')
    await asyncio.sleep(1.0)
    print(f'{time.ctime()} Goodbye!')

# asyncio provides a run() function to execute an async def function and all
# other coroutines called from there, like sleep() in the main() function.
asyncio.run(main())
