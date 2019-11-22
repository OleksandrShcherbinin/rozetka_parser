import os
import random
import asyncio
from time import sleep
from threading import Lock
from asyncio.queues import Queue
from requests_html import AsyncHTMLSession
from requests.exceptions import ConnectionError

LOCKER = Lock()

with open('new_users.txt', 'r', encoding='utf-8') as f:
    user_agents = f.read().split('\n')

with open('fresh_socks.txt', 'r', encoding='utf-8') as f:
    proxies_list = f.read().split('\n')


def filter_links(links):
    links = list(set(links[7:74]))
    bad_links = ('comments/', 'comments', 'ua/', 'list/', 'sellers/', '''#''', 'html',)
    good_links = [link for link in links if not link.endswith(bad_links)]
    return good_links


async def worker(qu, coro_num, session):
    while True:
        if qu.qsize() == 0:
            break
        url = await qu.get()
        try:
            print(f'[Send request in {coro_num}] [queue_size {qu.qsize()}]', url)
            prox = random.choice(proxies_list)
            proxies = {'http': prox, 'https': prox}
            headers = {'User-Agent': random.choice(user_agents)}

            response = await session.get(url, proxies=proxies, headers=headers, timeout=10)
            links = response.html.xpath('//div/a/@href')
            links_list = filter_links(links)

            for link in links_list:
                with LOCKER:
                    with open('notebook_links.txt', 'a') as f:
                        f.write(link + '\n')

            print('[Links saved]')
            del links_list, response

        except ConnectionError:
            await qu.put(url)
        except Exception as e:
            print(e, type(e))


async def main():
    category_queue = Queue()
    workers_count = 100
    category_base_url = 'https://rozetka.com.ua/ua/notebooks/c80004/page={}'

    for i in range(1, 100):
        cat_url = category_base_url.format(i)
        category_queue.put_nowait(cat_url)

    session = AsyncHTMLSession()

    tasks = []
    for num in range(workers_count):
        task = worker(category_queue, num, session)
        tasks.append(task)

    await asyncio.gather(*tasks)


if __name__ == '__main__':

    if os.path.exists("notebook_links.txt"):
        os.remove("notebook_links.txt")
        print('Deleted Old Links And Ready To Collect New!')
        sleep(1)
    elif not os.path.exists('notebook_links.txt'):
        print("There is no old links, I'll get new ones")

    asyncio.run(main())
    with open('notebook_links.txt', 'r', encoding='utf-8') as back_up:
        total_links = sum(1 for line in back_up)

    print(f'There Are {total_links} Fresh Links Collected To notebook_links.txt For Back-Up!')

    print('Now you can start your Rozetka_parser!')
