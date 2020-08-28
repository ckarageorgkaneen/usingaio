# Example 2-1. Best practice for threading
from concurrent.futures import ThreadPoolExecutor as Executor


def worker(data):
    print('<process the data>')


with Executor(max_workers=10) as exe:
    future = exe.submit(worker, 'data')
