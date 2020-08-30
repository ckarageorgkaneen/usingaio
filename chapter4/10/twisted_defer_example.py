# Example 4-10. Even more Twisted with inlined callbacks
from twisted.internet import defer


# Ordinarily, Twisted requires creating instances of Deferred and adding
# callbacks to those instances as the method of constructing async programs.
# A few years ago, the @inlineCallbacks decorator was added, which repurposes
# generators as coroutines.
@defer.inlineCallbacks
def f():
    yield
    # While @inlineCallbacks did allow you to write code that was linear in
    # appearance (unlike callbacks), some hacks were required, such as this
    # call to defer.returnValue(), which is how you have to return values from
    # @inlineCallbacks coroutines.
    defer.returnValue(123)


@defer.inlineCallbacks
def my_coro_func():
    # Here we can see the yield that makes this function a generator. For
    # @inlineCallbacks to work, there must be at least one yield present in
    # the function being decorated.
    value = yield f()
    assert value == 123
