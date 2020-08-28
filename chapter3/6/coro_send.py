async def f():
    return 123
coro = f()
try:
    # A coroutine is initiated by “sending” it a None. Internally, this is
    # what the event loop is going to be doing to your precious coroutines;
    # you will never have to do this manually. All the coroutines you make
    # will be executed either with loop.create_task(coro) or await coro. It’s
    # the loop that does the .send(None) behind the scenes.
    coro.send(None)
except StopIteration as e:
    # When the coroutine returns, a special kind of exception is raised,
    # called StopIteration . Note that we can access the return value of the
    # coroutine via the value attribute of the exception itself. Again, you
    # don’t need to know that it works like this: from your point of view,
    # async def functions will simply return a value with the return
    # statement, just like normal functions.
    print('The answer was:', e.value)
