import os
import psutil
import multiprocessing

# Here we can print to a csv easily


def worker():
    while True:
        print(
            f'cpu usage: {psutil.cpu_percent(interval=1, percpu=True)}')


def main():
    p = multiprocessing.Process(target=worker)
    p.daemon = True
    p.start()
    flag = True
    i = 0
    while flag:
        i += 1
        if i == 100000000:
            flag = False
            exit()
    p.join()


if __name__ == "__main__":
    main()
