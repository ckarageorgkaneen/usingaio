# Example 3-15. Checking completion status with done()
from asyncio import Future
f = Future()
print(f.done())
