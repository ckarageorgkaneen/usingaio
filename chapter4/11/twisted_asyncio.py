# Example 4-11. Support for asyncio in Twisted
from time import ctime
# This is how you tell Twisted to use the asyncio event loop as its main
# reactor. Note that this line must come before the reactor is imported from
# twisted.internet on the following line.

# from twisted.internet import asyncioreactor
# asyncioreactor.install()

# Anyone familiar with Twisted programming will recognize these imports. We
# don’t have space to cover them in depth here, but in a nutshell, the reactor
# is the Twisted version of the asyncio loop, and defer and task are
# namespaces for tools to work with scheduling coroutines.
from twisted.internet import reactor, defer, task


# Seeing async def here, in a Twisted program, looks odd, but this is indeed
# what the new support for async/await gives us: the ability to use native
# coroutines directly in Twisted programs.
async def main():
    for i in range(5):
        print(f'{ctime()} Hello {i}')
        # In the older @inlineCallbacks world, you would have used yield from
        # here, but now we can use await, the same as in asyncio code. The
        # other part of this line, deferLater(), is an alternative way to do
        # the same thing as asyncio.sleep(1). We await a future where, after
        # one second, a do-nothing callback will fire.
        await task.deferLater(reactor, 1, lambda: None)
# ensureDeferred() is a Twisted version of scheduling a coroutine. This would
# be analogous to loop.create_task() or asyncio.ensure_future().
defer.ensureDeferred(main())
# Running the reactor is the same as loop.run_forever() in asyncio.
reactor.run()
