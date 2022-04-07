import json
from urllib.parse import quote
import requests

base_url = 'http://192.168.31.1:9999/proxies/'
args = '/delay?timeout=5000&url=http://www.gstatic.com/generate_204'


def get_all_proxies():
    print('Healthy check start.')
    proxy_api = 'http://192.168.31.1:9999/proxies'
    data = requests.get(url=proxy_api).text
    proxies = json.loads(data).get('proxies')
    count = 0
    for key, value in proxies.items():
        if key == '♻️ 自动选择':
            for proxy in value.get('all')[:-1]:
                print("开始处理第 " + str(count) + "个请求...")
                print("proxy: " + proxy)
                api = base_url + quote(proxy) + args
                requests.get(url=api)
    print('Healthy check end.')


if __name__ == '__main__':
    get_all_proxies()
