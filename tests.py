import os
import multiprocessing as mp
import tqdm
import time


def sqmf(i):
    return 8000**i


if __name__ == '__main__':
    cpus = os.cpu_count()
    print(cpus-2)
    pl = mp.Pool(processes=(cpus - 2))
    results = []
    start = time.time()
    print(start)
    n = 1000000
    for _ in tqdm.tqdm(pl.map(sqmf, range(n)), n):
        results.append(_)
    pl.close()
    while True:
        if len(results) == n:
            print('done! time spent: {}'.format(time.time()-start))
            print(len(results))
            break
    pl.join()
