# Example 3-25. Async iterator for fetching data from Redis
import asyncio


# Mock Redis interface
class Redis:
    async def get(self, key):
        await asyncio.sleep(0)
        return 'value'


class OneAtATime:
    # The initializer of this class is quite ordinary: we store the Redis
    # connection instance and the list of keys to iterate over.
    def __init__(self, redis, keys):
        self.redis = redis
        self.keys = keys

    # Just as in the previous code example with __iter__() , we use
    # __aiter__() to set things up for iteration. We create a normal iterator
    # over the keys, self.ikeys, and return self because OneAtATime also
    # implements the __anext__() coroutine method.
    def __aiter__(self):
        self.ikeys = iter(self.keys)
        return self

    # Note that the __anext__() method is declared with async def , while the
    # __aiter__() method is declared only with def .
    async def __anext__(self):
        try:
            # For each key, we fetch the value from Redis: self.ikeys is a
            # regular iterator over the keys, so we use next() to move over
            # them.
            k = next(self.ikeys)
        # When self.ikeys is exhausted, we handle the StopIteration and simply
        # turn it into a StopAsyncIteration! This is how you signal stop from
        # inside an async iterator.
        except StopIteration:
            raise StopAsyncIteration
        # Finally—the entire point of this example—we can get the data from
        # Redis associated with this key. We can await the data, which means
        # that other code can run on the event loop while we wait on network
        # I/O.
        value = await self.redis.get(k)
        return value


# Mock create_redis
# Real one: aioredis.create_redis
async def create_redis(socket):
    await asyncio.sleep(0)
    return Redis()


async def do_something_with(value):
    await asyncio.sleep(0)


# The main() function: we run it using asyncio.run() toward the bottom of the
# code sample.
async def main():
    # We use the high-level interface in aioredis to get a connection.
    redis = await create_redis(('localhost', 6379))
    # Imagine that each of the values associated with these keys is quite
    # large and stored in the Redis instance.
    keys = ['Americas', 'Africa', 'Europe', 'Asia']
    # We’re using async for : the point is that iteration is able to suspend
    # itself while waiting for the next datum to arrive.
    async for value in OneAtATime(redis, keys):
        # For completeness, imagine that we also perform some I/O-bound
        # activity on the fetched value—perhaps a simple data transformation—
        # and then it gets sent on to another destination.
        await do_something_with(value)
asyncio.run(main())
