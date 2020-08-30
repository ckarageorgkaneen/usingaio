# Example 4-9. Message broker: improved design
import asyncio
from asyncio import StreamReader, StreamWriter, Queue
from collections import deque, defaultdict
from contextlib import suppress
from typing import Deque, DefaultDict, Dict
from msgproto import read_msg, send_msg


SUBSCRIBERS: DefaultDict[bytes, Deque] = defaultdict(deque)
SEND_QUEUES: DefaultDict[StreamWriter, Queue] = defaultdict(Queue)
# In the previous implementation, there were only SUBSCRIBERS ; now there are
# SEND_QUEUES and CHAN_QUEUES as global collections. This is a consequence of
# completely decoupling the receiving and sending of data. SEND_QUEUES has one
# queue entry for each client connection: all data that must be sent to that
# client must be placed onto that queue. (If you peek ahead, the send_client()
# coroutine will pull data off SEND_QUEUES and send it.)
CHAN_QUEUES: Dict[bytes, Queue] = {}


async def client(reader: StreamReader, writer: StreamWriter):
    peername = writer.get_extra_info('peername')
    subscribe_chan = await read_msg(reader)
    # Up until this point in the client() coroutine function, the code is the
    # same as in the simple server: the subscribed channel name is received,
    # and we add the StreamWriter instance for the new client to the global
    # SUBSCRIBERS collection.
    SUBSCRIBERS[subscribe_chan].append(writer)
    # This is new: we create a long-lived task that will do all the sending of
    # data to this client. The task will run independently as a separate
    # coroutine and will pull messages off the supplied queue,
    # SEND_QUEUES[writer], for sending.
    send_task = asyncio.create_task(
        send_client(writer, SEND_QUEUES[writer]))
    print(f'Remote {peername} subscribed to {subscribe_chan}')
    try:
        while channel_name := await read_msg(reader):
            data = await read_msg(reader)
            # Now we’re inside the loop where we receive data. Remember that
            # we always receive two messages: one for the destination channel
            # name, and one for the data. We’re going to create a new,
            # dedicated Queue for every destination channel, and that’s what
            # CHAN_QUEUES is for: when any client wants to push data to a
            # channel, we’re going to put that data onto the appropriate queue
            # and then go immediately back to listening for more data. This
            # approach decouples the distribution of messages from the
            # receiving of messages from this client.
            if channel_name not in CHAN_QUEUES:
                # If there isn’t already a queue for the target channel, make
                # one.
                CHAN_QUEUES[channel_name] = Queue(maxsize=10)
                # Create a dedicated and long-lived task for that channel. The
                # coroutine chan_sender() will be responsible for taking data
                # off the channel queue and distributing that data to
                # subscribers.
                asyncio.create_task(chan_sender(channel_name))
            # Place the newly received data onto the specific channel’s queue.
            # If the queue fills up, we’ll wait here until there is space for
            # the new data. Waiting here means we won’t be reading any new
            # data off the socket, which means that the client will have to
            # wait on sending new data into the socket on its side. This isn’t
            # necessarily a bad thing, since it communicates so-called
            # back-pressure to this client. (Alternatively, you could choose
            # to drop messages here if the use case is OK with that.)
            await CHAN_QUEUES[channel_name].put(data)
    except asyncio.CancelledError:
        print(f'Remote {peername} connection cancelled.')
    except asyncio.IncompleteReadError:
        print(f'Remote {peername} disconnected')
    finally:
        print(f'Remote {peername} closed')
        # When the connection is closed, it’s time to clean up. The long-lived
        # task we created for sending data to this client, send_task, can be
        # shut down by placing None onto its queue, SEND_QUEUES[writer] (check
        # the code for send_client() ). It’s important to use a value on the
        # queue, rather than outright cancellation, because there may already
        # be data on that queue and we want that data to be sent out before
        # send_client() is ended.
        await SEND_QUEUES[writer].put(None)
        # Wait for that sender task to finish...
        await send_task
        # ...then remove the entry in the SEND_QUEUES collection (and in the
        # next line, we also remove the sock from the SUBSCRIBERS collection
        # as before).
        del SEND_QUEUES[writer]
        SUBSCRIBERS[subscribe_chan].remove(writer)


# The send_client() coroutine function is very nearly a textbook example of
# pulling work off a queue. Note how the coroutine will exit only if None is
# placed onto the queue. Note also how we suppress CancelledError inside the
# loop: this is because we want this task to be closed only by receiving a
# None on the queue. This way, all pending data on the queue can be sent out
# before shutdown.
async def send_client(writer: StreamWriter, queue: Queue):
    while True:
        try:
            data = await queue.get()
        except asyncio.CancelledError:
            continue
        if not data:
            break
        try:
            await send_msg(writer, data)
        except asyncio.CancelledError:
            await send_msg(writer, data)
    writer.close()
    await writer.wait_closed()


async def chan_sender(name: bytes):
    with suppress(asyncio.CancelledError):
        while True:
            writers = SUBSCRIBERS[name]
            if not writers:
                await asyncio.sleep(1)
                # chan_sender() is the distribution logic for a channel: it
                # sends data from a dedicated channel Queue instance to all
                # the subscribers on that channel. But what happens if there
                # are no subscribers for this channel yet? We’ll just wait a
                # bit and try again. (Note, though, that the queue for this
                # channel, CHAN_QUEUES[name], will keep filling up.)
                continue
            # As in our previous broker implementation, we do something
            # special for channels whose name begins with /queue: we rotate
            # the deque and send only to the first entry. This acts like a
            # crude load-balancing system because each subscriber gets
            # different messages off the same queue. For all other channels,
            # all subscribers get all the messages.
            if name.startswith(b'/queue'):
                writers.rotate()
                writers = [writers[0]]
            # We’ll wait here for data on the queue, and exit if None is
            # received. Currently, this isn’t triggered anywhere (so these
            # chan_sender() coroutines live forever), but if logic were added
            # to clean up these channel tasks after, say, some period of
            # inactivity, that’s how it would be done.
            if not (msg := await CHAN_QUEUES[name].get()):
                break
            for writer in writers:
                if not SEND_QUEUES[writer].full():
                    print(f'Sending to {name}: {msg[:19]}...')
                    # Data has been received, so it’s time to send to
                    # subscribers. We do not do the sending here: instead, we
                    # place the data onto each subscriber’s own send queue.
                    # This decoupling is necessary to make sure that a slow
                    # subscriber doesn’t slow down anyone else receiving data.
                    # And furthermore, if the subscriber is so slow that their
                    # send queue fills up, we don’t put that data on their
                    # queue; i.e., it is lost.
                    await SEND_QUEUES[writer].put(msg)


async def main(*args, **kwargs):
    server = await asyncio.start_server(*args, **kwargs)
    async with server:
        await server.serve_forever()
try:
    asyncio.run(main(client, host='127.0.0.1', port=25000))
except KeyboardInterrupt:
    print('Bye!')
