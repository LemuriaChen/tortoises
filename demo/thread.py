
from multiprocessing import Process, Queue, Pool
import os
import time
import random


# def queue_demo(func):
#     def wrapper(*args, **kwargs):
#         print(f'fetch task from queue: {os.getpid()}')
#         func(*args, **kwargs)
#     return wrapper


# @queue_demo
def read(q):
    while True:
        if q.empty():
            return
        else:
            t = q.get()
            print(f'get {t} from queue, process ID < {os.getpid()} >')
            time.sleep(t / 10)


def run(num):

    start = time.time()
    queue_list = [random.randint(1, 4) for _ in range(100)]
    queue = Queue()

    for _ in queue_list:
        queue.put(_)

    processes = []
    for _ in range(num):
        processes.append(
            Process(target=read, args=(queue, ))
        )

    for process in processes:
        process.start()

    for process in processes:
        process.join()
    end = time.time()

    print(f'done. {round(end - start, 4)} seconds used.')


if __name__ == '__main__':

    # run(1)
    # run(2)
    # run(4)
    run(4)

