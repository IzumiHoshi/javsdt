# -*- coding:utf-8 -*-
import re
import requests
# from traceback import format_exc


# 用户指定jav321的网址后，请求jav所在网页，返回html
def get_321_html(url, proxy):
    for retry in range(10):
        try:
            if proxy:
                rqs = requests.get(url, proxies=proxy, timeout=(6, 7))
            else:
                rqs = requests.get(url, timeout=(6, 7))
        except requests.exceptions.ProxyError:
            # print(format_exc())
            print('    >通过局部代理失败...')
            continue
        except:
            print(f'    >打开网页失败，重新尝试...{url}')
            continue
        rqs.encoding = 'utf-8'
        rqs_content = rqs.text
        if re.search(r'JAV321', rqs_content):
            return rqs_content
        else:
            print('    >打开网页失败，空返回...重新尝试...')
            continue
    input(f'>>请检查你的网络环境是否可以打开: {url}')


# 向jav321 post车牌，得到jav所在网页，也可能是无结果的网页，返回html
def post_321_html(url, data, proxy):
    for retry in range(10):
        try:
            if proxy:
                rqs = requests.post(url, data=data, proxies=proxy, timeout=(6, 7))
            else:
                rqs = requests.post(url, data=data, timeout=(6, 7))
        except requests.exceptions.ProxyError:
            # print(format_exc())
            print('    >通过局部代理失败，重新尝试...')
            continue
        except:
            # print(format_exc())
            print(f'    >打开网页失败，重新尝试...{url}')
            continue
        rqs.encoding = 'utf-8'
        rqs_content = rqs.text
        if re.search(r'JAV321', rqs_content):
            return rqs_content
        else:
            print('    >打开网页失败，空返回...重新尝试...')
            continue
    input(f'>>请检查你的网络环境是否可以打开: {url}')
