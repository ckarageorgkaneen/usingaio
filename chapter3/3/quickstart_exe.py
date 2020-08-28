# Example 3 - 3. The basic executor interface
import time
import asyncio


async def main():
    print(f'{time.ctime()} Hello!')
    await asyncio.sleep(1.0)
    print(f'{time.ctime()} Goodbye!')


# blocking() calls the traditional time.sleep() internally, which would have
# blocked the main thread and prevented your event loop from running. This
# means that you must not make this function a coroutine—indeed, you cannot
# even call this function from anywhere in the main thread, which is where the
# asyncio loop is running. We solve this problem by running this function in an
# executor.
def blocking():
    # Unrelated to this section, but something to keep in mind for later in
    # the book: note that the blocking sleep time (0.5 seconds) is shorter
    # than the nonblocking sleep time (1 second) in the main() coroutine.
    # This makes the code sample neat and tidy. In “Waiting for the Executor
    # During Shutdown” on page 68 we’ll explore what happens if executor
    # functions outlive their async counterparts during the shutdown sequence.
    time.sleep(0.5)
    print(f'{time.ctime()} Hello from a thread!')


loop = asyncio.get_event_loop()
task = loop.create_task(main())
# This is the last of our list of essential, must-know features of asyncio . Sometimes
# you need to run things in a separate thread or even a separate process: this
# method is used for exactly that. Here we pass our blocking function to be run in
# the default executor. 4 Note that run_in_executor() does not block the main
# thread: it only schedules the executor task to run (it returns a Future , which
# means you can await it if the method is called within another coroutine func‐
# tion). The executor task will begin executing only after run_until_complete() is
# called, which allows the event loop to start processing events.
loop.run_in_executor(None, blocking)
loop.run_until_complete(task)
# Further to the note in callout 2: the set of tasks in pending does not include an
# entry for the call to blocking() made in run_in_executor() . This will be true of
# any call that returns a Future rather than a Task . The documentation is quite
# good at specifying return types, so you’ll see the return type there; just remember
# that all_tasks() really does return only Task s, not Future s.
pending = asyncio.all_tasks(loop=loop)
for task in pending:
    task.cancel()
group = asyncio.gather(*pending, return_exceptions=True)
loop.run_until_complete(group)
loop.close()
