# Example 3-37. Option A: wrap the executor call inside a coroutine
import time
import asyncio


async def main():
    loop = asyncio.get_running_loop()
    # The idea aims at fixing the shortcoming that run_in_executor() returns
    # only a Future instance and not a task. We can’t capture the job in
    # all_tasks() (used within asyncio.run()), but we can use await on the
    # future. The first part of the plan is to create a future inside the
    # main() function.
    future = loop.run_in_executor(None, blocking)
    try:
        print(f'{time.ctime()} Hello!')
        await asyncio.sleep(1.0)
        print(f'{time.ctime()} Goodbye!')
    finally:
        # We can use the try/finally structure to ensure that we wait for the
        # future to be finished before the main() function returns.
        await future


def blocking():
    time.sleep(2.0)
    print(f"{time.ctime()} Hello from a thread!")


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('Bye!')
