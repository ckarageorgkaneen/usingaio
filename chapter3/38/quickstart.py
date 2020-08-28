# Example 3-38. Option B: add the executor future to the gathered tasks
import time
import asyncio


# This utility function make_coro() simply waits for the future to complete—
# but crucially, it continues to wait for the future even inside the exception
# handler for CancelledError.
async def make_coro(future):
    try:
        return await future
    except asyncio.CancelledError:
        return await future


async def main():
    loop = asyncio.get_running_loop()
    future = loop.run_in_executor(None, blocking)
    # We take the future returned from the run_in_executor() call and pass it
    # into a new utility function, make_coro(). The important point here is
    # that we’re using create_task(), which means that this task will appear
    # in the list of all_tasks() within the shutdown handling of
    # asyncio.run(), and will receive a cancellation during the shutdown
    # process.
    asyncio.create_task(make_coro(future))
    print(f'{time.ctime()} Hello!')
    await asyncio.sleep(1.0)
    print(f'{time.ctime()} Goodbye!')


def blocking():
    time.sleep(2.0)
    print(f"{time.ctime()} Hello from a thread!")


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print('Bye!')
