import asyncio
import requests
import ujson
import uvloop
from unittest.mock import MagicMock
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor
from aiohttp import ClientSession, TCPConnector
from multiprocessing.pool import ThreadPool


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


func = MagicMock()


def error_callback(r):
    pass


def call_url():
    try:
        r = requests.get('https://subchat.site/api/v1/ping/', verify=False)
        data = ujson.loads(r.text)

        if data and data['status'] == 'ok':
            func()
    except Exception as e:
        error_callback(e)

def case_1():
    for _ in range(100):
        call_url()

def case_2():
    with ThreadPoolExecutor(max_workers=cpu_count()) as executor:
        for _ in range(100):
            executor.submit(call_url)


async def call_url_async():
    r = requests.get('https://subchat.site/api/v1/ping/', verify=False)
    data = ujson.loads(r.text)

    if data and data['status'] == 'ok':
        func()

async def case_3():
    await asyncio.gather(*[call_url_async() for _ in range(100)])


async def call_url_async_aiohttp():
    async with ClientSession(connector=TCPConnector(verify_ssl=False)) as session:
        async with session.get('https://subchat.site/api/v1/ping/') as response:
            response = await response.read()

    data = ujson.loads(response.decode('utf-8'))
    if data and data['status'] == 'ok':
        func()

async def case_4():
    await asyncio.gather(*[call_url_async_aiohttp() for _ in range(100)])

async def case_5():
    for _ in range(100):
        await call_url_async_aiohttp()


def case_6():
    pool = ThreadPool(cpu_count())
    for _ in range(100):
        pool.apply_async(call_url)
    pool.close()
    pool.join()
