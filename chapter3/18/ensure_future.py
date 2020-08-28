# Example 3-18. A closer look at what ensure_future() is doing
import asyncio


# A simple do-nothing coroutine function. We just need something that can make
# a coroutine.
async def f():
    pass
# We make the coroutine object by calling the function directly. Your code will
# rarely do this, but I want to be explicit here (a few lines down) that we’re
# passing a coroutine object into each of create_task() and ensure_future().
coro = f()
# Obtain the loop.
loop = asyncio.get_event_loop()
# First off, we use loop.create_task() to schedule our coroutine on the loop,
# and we get a new Task instance back.
task = loop.create_task(coro)
# We verify the type. So far, nothing interesting.
assert isinstance(task, asyncio.Task)
# We show that asyncio.ensure_future() can be used to perform the same act as
# create_task() : we passed in a coroutine and we got back a Task instance (and
# the coroutine has been scheduled to run on the loop)! If you’re passing in a
# coroutine, there is no difference between loop.create_task() and
# asyncio.ensure_future().
new_task = asyncio.ensure_future(coro)
assert isinstance(new_task, asyncio.Task)
# But what happens if we pass a Task instance to ensure_future()? Note that
# we’re passing in a Task instance that was already created by
# loop.create_task() in step 4.
mystery_meat = asyncio.ensure_future(task)
# We get back exactly the same Task instance as we passed in: it passes through
# unchanged.
assert mystery_meat is task
