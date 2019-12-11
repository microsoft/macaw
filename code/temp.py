a = None
if a:
    print('ddd')

from multiprocessing import Pool, TimeoutError
import time
import os
from func_timeout import func_timeout, FunctionTimedOut
import multiprocessing


def f(x):
    time.sleep(x)
    return x

def run_action(x, y):
    try:
        return func_timeout(4, f, args=[x + y])
    except FunctionTimedOut:
        return None

if __name__ == '__main__':
    action_processes = []
    start = time.time()
    pool = multiprocessing.Pool(processes=20)
    args = [[i, 1] for i in range(10)]
    print(pool.starmap(run_action, args))

    print(time.time()-start)
    # for i in range(10):
    #     p = multiprocessing.Process(target=run_action, args=[i])
    #     action_processes.append(p)
    #     p.start()

    # for p in action_processes:
    #     p.start()

    # for p in action_processes:
    #     p.join()
    #
    # for p in action_processes:
    #     print(p.)