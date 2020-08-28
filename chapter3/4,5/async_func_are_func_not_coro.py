# Example 3-4. Async functions are functions, not coroutines
import inspect

# This is the simplest possible declaration of a coroutine: it looks like a
# regular function, except that it begins with the keywords async def.


async def f():
    return 123

# Surprise! The precise type of f is not “coroutine”; it’s just an ordinary
# function. While it is common to refer to async def functions as coroutines,
# strictly speaking they are considered by Python to be coroutine functions.
# This behavior is identical to the way generator functions work in Python:
# >>> def g():
# ...
# yield 123
# ...
# >>> type(g)
# <class 'function'>
# >>> gen = g()
# >>> type(gen)
# <class 'generator'>
# Even though g is sometimes incorrectly referred to as a “generator,” it
# remains a function, and it is only when this function is evaluated that
# the generator is returned. Coroutine functions work in exactly the same
# way: you need to call the async def function to obtain the coroutine object.
print(type(f))
# The inspect module in the standard library can provide much better introspec‐
# tive capabilities than the type() built-in function.
# There is an iscoroutinefunction() function that lets you distinguish between
# an ordinary function and a coroutine function.
print(inspect.iscoroutinefunction(f))

# Example 3-5. An async def function returns a coroutine object
coro = f()
print(type(coro))
print(inspect.iscoroutine(coro))
