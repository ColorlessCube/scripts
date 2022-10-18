import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote
import requests
from logger import logger

base_url = 'http://192.168.31.1:9999/proxies/'
args = '/delay?timeout=5000&url=http://www.gstatic.com/generate_204'
max_workers = 8


def ping_proxy(proxy):
    api = base_url + quote(proxy) + args
    requests.get(url=api)
    return proxy


def get_all_proxies():
    logger.info('Healthy check start.')
    proxy_api = 'http://192.168.31.1:9999/proxies'
    data = requests.get(url=proxy_api).text
    proxies = json.loads(data).get('proxies')
    futures = []
    pool = ThreadPoolExecutor(max_workers=max_workers)
    for key, value in proxies.items():
        if key == '♻️ 自动选择':
            for proxy in value.get('all')[:-1]:
                futures.append(pool.submit(ping_proxy, proxy))
    for future in as_completed(futures):
        proxy = future.result()
        logger.info('Healthy check --- {} ping succeed.'.format(proxy))
    logger.info('Healthy check end.')


if __name__ == '__main__':
    get_all_proxies()
