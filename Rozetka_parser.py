import random
import asyncio
from asyncio.queues import Queue
from requests_html import AsyncHTMLSession
from requests.exceptions import ConnectionError
from notebooksDB import Ad, connection
from aiopg.sa import create_engine
from time import time
from datetime import datetime

with open('new_users.txt', 'r', encoding='utf-8') as f:
    user_agents = f.read().split('\n')

with open('fresh_socks.txt', 'r', encoding='utf-8') as f:
    proxies_list = f.read().split('\n')


def filter_picture(picture):
    good_pics = []
    for pic in picture:
        if pic.endswith('.jpg'):
            good_pics.append(pic)
        else:
            continue
    return str(good_pics).strip('[]').replace("'", '').replace(",", '\n')


async def worker(qu, coro_num, session, engine):
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
            name = resp.html.xpath('//div/h1/text()')
            status = resp.html.xpath('//div[@class="detail-status"]/text()')
            if status == []:
                status = 'Є в наявності'
            elif status == ['\n']:
                status = 'Не маэ'
            else:
                status = 'Закінчується'
            price = resp.html.xpath('//*[@itemprop="price"]/@content')
            picture = resp.html.xpath('//div/a/@href')
            pics = filter_picture(picture)
            description = resp.html.xpath('//div[@class="b-rich-text text-description-content box-hide"]'
                                          '//p//text()')
            procesor = resp.html.xpath('//div/span/a/text()')

            name = str(name).replace('''\\n''', '').replace("'", '').replace("[", '').replace("]", '')
            description = str(description).replace("'", '').replace("[", '').replace("]", '')

            ad_dict = {
                'date': datetime.now().date(),
                'name': name,
                'status': status,
                'price': price[0],
                'procesor': procesor[2],
                'diagonal': procesor[3],
                'memory': procesor[4],
                'OS': procesor[5],
                'procesor gen': procesor[6],
                'color': procesor[7],
                'optic drive': procesor[8],
                'HDD': procesor[9],
                'picture': pics,
                'description': description
            }
            async with engine.acquire() as cursor:
                sql = Ad.insert().values(**ad_dict)
                await cursor.execute(sql)
            print('[Ad saved]', ad_dict["name"], ad_dict["price"], ad_dict["status"])
        except ConnectionError:
            await qu.put(link)
        except Exception as e:
            print(e, type(e))


async def main():
    category_queue = Queue()
    workers_count = 100
    with open('notebook_links.txt', 'r', encoding='utf-8') as f:
        links = f.read().split('\n')
        for link in links:
            category_queue.put_nowait(link)

        session = AsyncHTMLSession()
        engine1 = await create_engine(**connection)

        tasks = []
        for num in range(workers_count):
            task = worker(category_queue, num, session, engine1)
            tasks.append(task)

        await asyncio.gather(*tasks)


if __name__ == '__main__':
    t1 = time()
    asyncio.run(main())
    t2 = time()
    print('Время парсинга', (t2-t1)/60)