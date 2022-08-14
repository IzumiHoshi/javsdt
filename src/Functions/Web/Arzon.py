# -*- coding:utf-8 -*-
import requests
import re
# from traceback import format_exc
from Class.MyEnum import ScrapeStatusEnum
from Functions.Progress.Prepare import write_new_arzon_phpsessid


# 功能: 获取一个arzon_cookie
# 参数: 代理proxy
# 返回: cookies
def steal_arzon_cookies(proxy):
    print('\n正在尝试通过 https://www.arzon.jp 的成人验证...')
    for retry in range(10):
        try:    # 当初费尽心机，想办法如何通过页面上的成人验证，结果在一个C#开发的jav爬虫项目，看到它请求以下网址，再跳转到arzon主页，所得到的的cookie即是合法的cookie
            if proxy:
                session = requests.Session()
                session.get('https://www.arzon.jp/index.php?action=adult_customer_agecheck&agecheck=1&redirect=https'
                            '%3A%2F%2Fwww.arzon.jp%2F', proxies=proxy, timeout=(12, 7))
                print('通过arzon的成人验证！\n')
                return session.cookies.get_dict()
            else:
                session = requests.Session()
                session.get('https://www.arzon.jp/index.php?action=adult_customer_agecheck&agecheck=1&redirect=https'
                            '%3A%2F%2Fwww.arzon.jp%2F', timeout=(12, 7))
                print('通过arzon的成人验证！\n')
                return session.cookies.get_dict()
        except requests.exceptions.ProxyError:
            # print(format_exc())
            print('    >通过局部代理失败，重新尝试...')
            continue
        except:
            # print(format_exc())
            print('通过失败，重新尝试...')
            continue
    input('>>请检查你的网络环境是否可以打开: https://www.arzon.jp/')


# 功能: 搜索arzon，或请求arzon上jav所在网页
# 参数: 网址url，请求头部header/cookies，代理proxy
# 返回: 网页html
def get_arzon_html(url, cookies, proxy):
    # print('代理: ', proxy)
    for retry in range(10):
        try:
            if proxy:
                rqs = requests.get(url, cookies=cookies, proxies=proxy, timeout=(12, 7))
            else:
                rqs = requests.get(url, cookies=cookies, timeout=(12, 7))
        except requests.exceptions.ProxyError:
            # print(format_exc())
            print('    >通过局部代理失败，重新尝试...')
            continue
        except:
            print(f'    >打开网页失败，重新尝试...{url}')
            continue
        rqs.encoding = 'utf-8'
        rqs_content = rqs.text
        if re.search(r'arzon', rqs_content):
            return rqs_content
        else:
            print('    >打开网页失败，空返回...重新尝试...')
            continue
    input(f'>>请检查你的网络环境是否可以打开: {url}')


# 功能: 从arzon上查找简介
# 参数: 车牌car，cookies，proxy
# 返回: 简介，执行完成状态码，cookies
def scrape_from_arzon(jav_file, jav_model, cookies, proxy):
    for retry in range(2):
        url_search_arzon = f'https://www.arzon.jp/itemlist.html?t=&m=all&s=&q={jav_file.Car_id.replace("-", "")}'
        print('    >搜索arzon: ', url_search_arzon)
        # 得到arzon的搜索结果页面
        html_search_arzon = get_arzon_html(url_search_arzon, cookies, proxy)
        # <dt><a href="https://www.arzon.jp/item_1376110.html" title="限界集落 ～村民"><img src=
        list_search_results = re.findall(r'h2><a href="/item_(.+?)\.html" title=', html_search_arzon)  # 所有搜索结果链接
        # 搜索结果为N个AV的界面
        if list_search_results:  # arzon有搜索结果
            for url_each_result in list_search_results:
                url_jav = f'https://www.arzon.jp/item_{url_each_result}.html'  # 第i+1个链接
                print('    >获取简介: ', url_jav)
                # 打开arzon上每一个搜索结果的页面
                html_jav_arzon = get_arzon_html(url_jav, cookies, proxy)
                # 在该url_jav网页上查找简介
                plotg = re.search(r'h2>作品紹介</h2>([\s\S]*?)</div>', html_jav_arzon)
                # 成功找到plot
                if plotg:
                    plot_br = plotg.group(1)
                    plot = ''
                    for line in plot_br.split('<br />'):
                        line = line.strip()
                        plot = f'{plot}{line}'
                    jav_model.Arzon = url_each_result
                    jav_model.Plot = plot
                    return ScrapeStatusEnum.success, cookies
            # 几个搜索结果查找完了，也没有找到简介
            jav_model.Plot = '【arzon有该影片，但找不到简介】'
            return ScrapeStatusEnum.arzon_exist_but_no_plot, cookies
        # 没有搜索结果
        else:
            # arzon返回的页面实际是18岁验证
            adultg = re.search(r'１８歳未満', html_search_arzon)
            if adultg:
                cookies = steal_arzon_cookies(proxy)
                write_new_arzon_phpsessid(cookies['PHPSESSID'])
                continue
            # 不是成人验证，也没有简介
            else:
                jav_model.Plot = '【影片下架，暂无简介】'
                return ScrapeStatusEnum.arzon_not_found, cookies
    input('>>请检查你的网络环境是否可以通过成人验证: https://www.arzon.jp/')
    return ScrapeStatusEnum.interrupted, cookies
