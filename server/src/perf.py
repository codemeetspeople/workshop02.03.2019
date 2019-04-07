import sys
import requests
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count

class Count:
    count = 0


def ping():
    requests.get('http://127.0.0.1:8080/api/v1/ping/')
    Count.count += 1
    sys.stdout.write(f'requests count: {Count.count}\r')
    sys.stdout.flush()


def send10krequests(func=ping):
    for _ in range(10000):
        func()


with ThreadPoolExecutor(max_workers=cpu_count()) as executor:
    for _ in range(cpu_count()):
        executor.submit(send10krequests)