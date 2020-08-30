# Example 4-19. The collection layer: this server collects process stats
import os
import asyncio
import zmq
import zmq.asyncio
import aiohttp
import json
from contextlib import suppress
from aiohttp import web
from aiohttp_sse import sse_response
from weakref import WeakSet


CHARTS_HTML_FILE_PATH = os.path.join(os.path.dirname(os.path.realpath(
    __file__)), '../../appendixB/3/charts.html')

# zmq.asyncio.install()
ctx = zmq.asyncio.Context()
# One half of this program will receive data from other applications, and the
# other half will provide data to browser clients via server-sent events
# (SSEs). I use a WeakSet() to keep track of all the currently connected web
# clients. Each connected client will have an associated Queue() instance, so
# this connections identifier is really a set of queues.
connections = WeakSet()


async def collector():
    # Recall that in the application layer, I used a zmq.PUB socket; here in
    # the collection layer, I use its partner, the zmq.SUB socket type. This
    # ØMQ socket can only receive, not send.
    sock = ctx.socket(zmq.SUB)
    # For the zmq.SUB socket type, providing a subscription name is required,
    # but for our purposes, we’ll just take everything that comes in—hence the
    # empty topic name.
    sock.setsockopt_string(zmq.SUBSCRIBE, '')
    # I bind the zmq.SUB socket. Think about that for second. In pub-sub
    # configurations, you usually have to make the pub end the server (bind())
    # and the sub end the client (connect()). ØMQ is different: either end can
    # be the server. For our use case, this is important, because each of our
    # application-layer instances will be connecting to the same collection
    # server domain name, and not the other way around.
    sock.bind('tcp://*:5555')
    with suppress(asyncio.CancelledError):
        # The support for asyncio in pyzmq allows us to await data from our
        # connected apps. And not only that, but the incoming data will be
        # automatically deserialized from JSON (yes, this means data is a
        # dict()).
        while data := await sock.recv_json():
            print(data)
            for q in connections:
                # Recall that our connections set holds a queue for every
                # connected web client. Now that data has been received, it’s
                # time to send it to all the clients: the data is placed onto
                # each queue.
                await q.put(data)
    sock.close()


# The feed() coroutine function will create coroutines for each connected web
# client. Internally, server-sent events are used to push data to the web
# clients.
async def feed(request):
    queue = asyncio.Queue()
    # As described earlier, each web client will have its own queue instance,
    # in order to receive data from the collector() coroutine. The queue
    # instance is added to the connections set, but because connections is a
    # weak set, the entry will automatically be removed from connections when
    # the queue goes out of scope—i.e., when a web client disconnects.
    # Weakrefs are great for simplifying these kinds of bookkeeping tasks.
    connections.add(queue)
    with suppress(asyncio.CancelledError):
        # The aiohttp_sse package provides the sse_response() context manager.
        # This gives us a scope inside which to push data to the web client.
        async with sse_response(request) as resp:
            # We remain connected to the web client, and wait for data on this
            # specific client’s queue.
            while data := await queue.get():
                print('sending data:', data)
                # As soon as the data comes in (inside collector() ), it will
                # be sent to the connected web client. Note that I reserialize
                # the data dict here. An optimization to this code would be to
                # avoid deserializing JSON in collector() , and instead use
                # sock.recv_string() to avoid the serialization round trip. Of
                # course, in a real scenario, you might want to deserialize in
                # the collector, and perform some validation on the data
                # before sending it to the browser client. So many choices!
                await resp.send(json.dumps(data))
    return resp


# The index() endpoint is the primary page load, and here we serve a static
# file called charts.html.
async def index(request):
    return aiohttp.web.FileResponse(CHARTS_HTML_FILE_PATH)


# The aiohttp library provides facilities for us to hook in additional
# long-lived coroutines we might need. With the collector() coroutine, we have
# exactly that situation, so I create a startup coroutine, start_collector(),
# and a shutdown coroutine. These will be called during specific phases of
# aiohttp’s startup and shutdown sequence. Note that I add the collector task
# to the app itself, which implements a mapping protocol so that you can use
# it like a dict.
async def start_collector(app):
    loop = asyncio.get_event_loop()
    app['collector'] = loop.create_task(collector())


async def stop_collector(app):
    print('Stopping collector...')
    # I obtain our collector() coroutine off the app identifier and call
    # cancel() on that.
    app['collector'].cancel()
    await app['collector']
    ctx.term()

if __name__ == '__main__':
    app = web.Application()
    app.router.add_route('GET', '/', index)
    app.router.add_route('GET', '/feed', feed)
    # Finally, you can see where the custom startup and shutdown coroutines
    # are hooked in: the app instance provides hooks to which our custom
    # coroutines may be appended.
    app.on_startup.append(start_collector)
    app.on_cleanup.append(stop_collector)
    web.run_app(app, host='127.0.0.1', port=8088)
