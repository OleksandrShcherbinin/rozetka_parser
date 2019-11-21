import os
import random
import asyncio
from time import time
from threading import Lock
from asyncio.queues import Queue
from requests_html import AsyncHTMLSession
from requests.exceptions import ConnectionError
from sqlalchemy import create_engine

LOCKER = Lock()

with open('new_users.txt', 'r', encoding='utf-8') as f:
    user_agents = f.read().split('\n')

with open('fresh_socks.txt', 'r', encoding='utf-8') as f:
    proxies_list = f.read().split('\n')

NUM = 0


async def worker(qu, coro_num, session):

    while True:
        if qu.qsize() == 0:
            break
        link = await qu.get()
        try:
            print(f'[Send request in {coro_num}] [queue_size {qu.qsize()}]', link)
            prox = random.choice(proxies_list)
            proxies = {'http': prox, 'https': prox}
            headers = {'User-Agent': random.choice(user_agents)}
            resp = await session.get(link, proxies=proxies, headers=headers, timeout=10)
            with LOCKER:
                global NUM
                NUM += 1
                if NUM == 101:
                    print('ENOUGH')
                    quit()
                # Make sure you create a folder for picture files to be collected
                # And put it here in os.path.join
                with open(os.path.join(f'd:/Rozetka_pics/rozetka_pic{NUM}.jpg'), 'wb') as file:
                    file.write(resp.content)
                    print(f'[File Saved]{NUM}')

        except ConnectionError:
            await qu.put(link)
        except Exception as e:
            print(e, type(e))


async def main():

    pictures_queue = Queue()
    workers_count = 300
    connection = {
        'user': 'Your user name',  # input your postgres username
        'database': 'your database name',  # input your database name here
        'host': '127.0.0.1',  # change your host if it's not local
        'password': 'your password'  # input your password for this database
    }
    dsn = 'postgresql://{user}:{password}@{host}/{database}'.format(**connection)

    engine = create_engine(dsn)
    result = engine.execute('''select picture from "your_table_name"''')
    res_list = []
    for row in result:
        clean_jpg = row['picture'].split("\n")
        for i in clean_jpg:
            res_list.append(i)
    print(len(res_list))

    for pic in res_list:
        pictures_queue.put_nowait(pic)

    session = AsyncHTMLSession()

    tasks = []
    for num in range(workers_count):
        task = worker(pictures_queue, num, session)
        tasks.append(task)
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    t1 = time()
    asyncio.run(main())
    t2 = time()
    print('Время записи файлов', (t2-t1)/60)