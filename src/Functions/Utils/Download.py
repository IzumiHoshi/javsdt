# -*- coding:utf-8 -*-
import requests
from PIL import Image


# 下载图片，无返回
# 参数: 图片地址，存放路径，代理
def download_pic(url, path, proxy):
    for retry in range(5):
        try:
            if proxy:
                rqs = requests.get(url, proxies=proxy, stream=True, timeout=(6, 10))
                with open(path, 'wb') as pic:
                    for chunk in rqs:
                        pic.write(chunk)
            else:
                rqs = requests.get(url, stream=True, timeout=(6, 10))
                with open(path, 'wb') as pic:
                    for chunk in rqs:
                        pic.write(chunk)
        except requests.exceptions.ProxyError:
            # print(format_exc())
            print('    >通过局部代理失败，重新尝试...')
            continue
        except:
            # print(format_exc())
            print('    >下载失败，重新下载...')
            continue
        # 如果下载的图片打不开，则重新下载
        try:
            img = Image.open(path)
            img.load()
            print('    >fanart.jpg下载成功')
            return True
        except OSError:
            print('    >下载失败，重新下载....')
            continue
    return False
