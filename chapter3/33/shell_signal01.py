# Example 3-33. Refresher for using KeyboardInterrupt as a SIGINT handler
import asyncio


# This is the main part of our application. To keep things simple, we’re just
# going to sleep in an infinite loop.
async def main():
    while True:
        print('<Your app is running>')
        await asyncio.sleep(1)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # This startup and shutdown sequence will be familiar to you from the
    # previous section. We schedule main(), call run_forever(), and wait for
    # something to stop the loop.
    task = loop.create_task(main())
    try:
        loop.run_until_complete(task)
    # In this case, only Ctrl-C will stop the loop. Then we handle
    # KeyboardInterrupt and do all the necessary cleanup bits, as covered in
    # the previous sections.
    except KeyboardInterrupt:
        print('Got signal: SIGINT, shutting down.')
    tasks = asyncio.all_tasks(loop=loop)
    for t in tasks:
        t.cancel()
    group = asyncio.gather(*tasks, return_exceptions=True)
    loop.run_until_complete(group)
    loop.close()
