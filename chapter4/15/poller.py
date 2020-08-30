# Example 4-15. The traditional ØMQ approach
import zmq
context = zmq.Context()
# ØMQ sockets have types. This is a PULL socket. You can think of it as a
# receive-only kind of socket that will be fed by some other send-only socket,
# which will be a PUSH type.
receiver = context.socket(zmq.PULL)
receiver.connect("tcp://localhost:5557")
# The SUB socket is another kind of receive-only socket, and it will be fed a
# PUB socket which is send-only.
subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://localhost:5556")
subscriber.setsockopt_string(zmq.SUBSCRIBE, '')
# If you need to move data between multiple sockets in a threaded ØMQ
# application, you’re going to need a poller. This is because these sockets
# are not thread-safe, so you cannot recv() on different sockets in different
# threads.
poller = zmq.Poller()
poller.register(receiver, zmq.POLLIN)
poller.register(subscriber, zmq.POLLIN)
while True:
    try:
        # It works similarly to the select() system call. The poller will
        # unblock when there is data ready to be received on one of the
        # registered sockets, and then it’s up to you to pull the data off and
        # do something with it. The big if block is how you detect the correct
        # socket.
        socks = dict(poller.poll())
    except KeyboardInterrupt:
        break
    if receiver in socks:
        message = receiver.recv_json()
        print(f'Via PULL: {message}')
    if subscriber in socks:
        message = subscriber.recv_json()
        print(f'Via SUB: {message}')
