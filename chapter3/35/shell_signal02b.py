# Example 3-35. Signal handling when using asyncio.run()
import asyncio
from signal import SIGINT, SIGTERM


async def main():
    loop = asyncio.get_running_loop()
    for sig in (SIGTERM, SIGINT):
        # Because asyncio.run() takes control of the event loop startup, our
        # first opportunity to change signal handling behavior will be in the
        # main() function.
        loop.add_signal_handler(sig, handler, sig)
    try:
        while True:
            print('<Your app is running>')
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        for i in range(3):
            print('<Your app is shutting down...>')
            await asyncio.sleep(1)


def handler(sig):
    loop = asyncio.get_running_loop()
    # Inside the signal handler, we can’t stop the loop as in previous
    # examples, because we’ll get warnings about how the loop was stopped
    # before the task created for main() was completed. Instead, we can
    # initiate task cancellation here, which will ultimately result in the
    # main() task exiting; when that happens, the cleanup handling inside
    # asyncio.run() will take over.
    for task in asyncio.all_tasks(loop=loop):
        task.cancel()
    print(f'Got signal: {sig!s}, shutting down.')
    loop.remove_signal_handler(SIGTERM)
    loop.add_signal_handler(SIGINT, lambda: None)


if __name__ == '__main__':
    asyncio.run(main())
