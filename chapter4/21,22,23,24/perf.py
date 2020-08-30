# Example B-5. perf.py
import logging
from time import perf_counter
from inspect import iscoroutinefunction

logger = logging.getLogger('perf')
logging.basicConfig(level=logging.INFO)


# The aelapsed() decorator will record the time taken to execute the wrapped
# coroutine.
def aelapsed(corofn, caption=''):
    async def wrapper(*args, **kwargs):
        t0 = perf_counter()
        result = await corofn(*args, **kwargs)
        delta = (perf_counter() - t0) * 1e3
        logger.info(
            f'{caption} Elapsed: {delta:.2f} ms')
        return result
    return wrapper


# The aprofiler() metaclass will make sure that every member of the class that
# is a coroutine function will get wrapped in the aelapsed() decorator.
def aprofiler(cls, bases, members):
    for k, v in members.items():
        if iscoroutinefunction(v):
            members[k] = aelapsed(v, k)
    return type.__new__(type, cls, bases, members)
