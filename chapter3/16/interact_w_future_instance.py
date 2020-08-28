# Example 3-16. Interaction with a Future instance
import asyncio


# Create a simple main function. We can run this, wait for a bit, and then set
# a result on this Future, f.
async def main(f: asyncio.Future):
    await asyncio.sleep(1)
    # Set the result.
    f.set_result('I have finished.')
loop = asyncio.get_event_loop()
# Manually create a Future instance. Note that this instance is (by default)
# tied to our loop, but it is not and will not be attached to any coroutine
# (that’s what Tasks are for).
fut = asyncio.Future()
# Before doing anything, verify that the future is not done yet.
print(fut.done())
# Schedule the main() coroutine, passing the future. Remember, all the main()
# coroutine does is sleep and then toggle the Future instance. (Note that the
# main() coroutine will not start running yet: coroutines run only when the
# loop is running.)
loop.create_task(main(fut))
# Here we use run_until_complete() on a Future instance, rather than a Task
# instance. 7 This is different from what you’ve seen before. Now that the
# loop is running, the main() coroutine will begin executing.
loop.run_until_complete(fut)
print(fut.done())
# Eventually, the future completes when its result is set. After completion,
# the result can be accessed.
print(fut.result())
