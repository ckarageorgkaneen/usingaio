# Example 3-23. The nonblocking-with-a-little-help-from-my-friends way
import asyncio
from contextlib import asynccontextmanager


def download_webpage(url):
    class Data:
        pass
    return Data()


def update_stats(url):
    pass


def process(data):
    pass


@asynccontextmanager
# For this example, assume that we are unable to modify the code for our two
# blocking calls, download_webpage() and update_stats() ; i.e., we can’t alter
# them to be coroutine functions. That’s bad, because the most grave sin of
# event-based programming is breaking the rule that you must never, under any
# circumstances, prevent the event loop from processing events.
# To get around the problem, we will use an executor to run the blocking calls
# in a separate thread. The executor is made available to us as an attribute
# of the event loop itself.
async def web_page(url):
    loop = asyncio.get_event_loop()
    # We call the executor. The signature is
    # AbstractEventLoop.run_in_executor (executor, func, *args). If you want
    # to use the default executor (which is a ThreadPoolExecutor), you must
    # pass None as the value for the executor argument.
    data = await loop.run_in_executor(
        None, download_webpage, url)
    yield data
    # As with the call to download_webpage(), we also run the other blocking
    # call to update_stats() in an executor. Note that you must use the await
    # keyword in front. If you forget, the execution of the asynchronous
    # generator (i.e., your async context manager) will not wait for the call
    # to complete before proceeding.
    await loop.run_in_executor(None, update_stats, url)


async def main():
    async with web_page('google.com') as data:
        process(data)
asyncio.run(main())
