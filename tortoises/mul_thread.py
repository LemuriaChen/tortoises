
from multiprocessing import Process, Queue
# import os
import time
import random


class ProcessWrapper(object):

    def __init__(self, func, tasks: list, num_workers: int):
        self.func = func
        self.tasks = tasks
        self.num_workers = num_workers
        self.queue = Queue()
        self.processes = []
        self.to_queue()

    def to_queue(self):
        for item in self.tasks:
            self.queue.put(item)

    def run(self):
        start = time.time()
        # create multiple process
        for _ in range(self.num_workers):
            self.processes.append(
                Process(target=self.my_fun)
            )
        for p in self.processes:
            p.start()
        for p in self.processes:
            p.join()
        end = time.time()
        print(f'done. {round(end - start, 4)} seconds used.')

    def my_fun(self, ):
        while True:
            if self.queue.empty():
                return
            else:
                item = self.queue.get()
                self.func(item)


if __name__ == '__main__':

    def print_and_sleep(t):
        # print(f'get {t} from queue, process ID < {os.getpid()} >')
        time.sleep(t / 10)

    x = [random.randint(1, 4) for _ in range(100)]
    pw = ProcessWrapper(print_and_sleep, x, 10)
    pw.run()
