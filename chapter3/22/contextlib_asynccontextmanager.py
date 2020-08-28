# Example 3-22. The nonblocking way
import asyncio
from contextlib import asynccontextmanager


async def download_webpage(url):
    class Data:
        pass
    await asyncio.sleep(0)
    return Data()


async def update_stats(url):
    await asyncio.sleep(0)


def process(data):
    pass


# The new @asynccontextmanager decorator is used in exactly the same way.
@asynccontextmanager
# It does, however, require that the decorated generator function be declared
# with async def.
async def web_page(url):
    # As before, we fetch the data from the URL before making it available to
    # the body of the context manager. I have added the await keyword, which
    # tells us that this coroutine will allow the event loop to run other
    # tasks while we wait for the network call to complete.
    #
    # Note that we cannot simply tack on the await keyword to anything. This
    # change presupposes that we were also able to modify the
    # download_webpage() function itself, and convert it into a coroutine that
    # is compatible with the await keyword. For the times when it is not
    # possible to modify the function, a different approach is needed; we’ll
    # discuss that in the next example.
    data = await download_webpage(url)
    # As before, the data is made available to the body of the context
    # manager. I’m trying to keep the code simple, so I’ve omitted the usual
    # try/finally handler that you should normally write to deal with
    # exceptions raised in the body of caller.
    #
    # Note that the presence of yield is what changes a function into a
    # generator function; the additional presence of the async def keywords in
    # point 1 makes this an asynchronous generator function. When called, it
    # will return an asynchronous generator. The inspect module has two
    # functions that can test for these: isasyncgenfunction() and
    # isasyncgen(), respectively.
    yield data
    # Here, assume that we’ve also converted the code inside the update
    # stats() function to allow it to produce coroutines. We can then use the
    # await keyword, which allows a context switch to the event loop while we
    # wait for the I/O-bound work to complete.
    await update_stats(url)


async def main():
    # Another change was required in the usage of the context manager itself:
    # we needed to use async with instead of a plain with.
    async with web_page('google.com') as data:
        process(data)
asyncio.run(main())
