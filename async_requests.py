import requests
import asyncio
import aiohttp
import time

MAX_REQUESTS_PER_SECOND = 20
REQUEST_INTERVAL = 1 / MAX_REQUESTS_PER_SECOND
last_request_time = 0


async def request_page(session, url, text_callback, *args, **kwargs):
    global last_request_time

    ticks = 0
    time_from_request = time.time() - last_request_time
    while time_from_request < REQUEST_INTERVAL:
        await asyncio.sleep(REQUEST_INTERVAL - time_from_request)
        time_from_request = time.time() - last_request_time
    
    last_request_time = time.time()

    async with session.get(url) as response:
        text_callback(await response.text(), *args, **kwargs)


async def parse_pages_batch(pages):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i, page in enumerate(pages):
            tasks.append(request_page(session, page[0], page[1], *page[2], **page[3]))
        await asyncio.gather(*tasks)

