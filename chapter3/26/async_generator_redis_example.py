# Example 3-26. Easier with an async generator
import asyncio


# Mock Redis interface
class Redis:
    async def get(self, key):
        await asyncio.sleep(0)
        return 'value'


# Mock create_redis
# Real one: aioredis.create_redis
async def create_redis(socket):
    await asyncio.sleep(0)
    return Redis()


async def do_something_with(value):
    await asyncio.sleep(0)


# Our function is now declared with async def , making it a coroutine
# function, and since this function also contains the yield keyword, we refer
# to it as an asynchronous generator function.
async def one_at_a_time(redis, keys):
    for k in keys:
        # We don’t have to do the convoluted things necessary in the previous
        # example with self.ikeys: here, we just loop over the keys directly
        # and obtain the value...
        value = await redis.get(k)
        # ...and then yield it to the caller, just like a normal generator.
        yield value


# The main() function is identical to the version in Example 3-25.
async def main():
    redis = await create_redis(('localhost', 6379))
    keys = ['Americas', 'Africa', 'Europe', 'Asia']
    async for value in one_at_a_time(redis, keys):
        await do_something_with(value)
asyncio.run(main())
