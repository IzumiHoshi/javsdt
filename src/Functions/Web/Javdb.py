# -*- coding:utf-8 -*-
from math import ceil
import re
from lxml import etree

import requests
# from traceback import format_exc

from Functions.Metadata.Car import extract_number_from_car_suf, extract_number_from_car
from Class.MyEnum import ScrapeStatusEnum
from Class.MyError import SpecifiedUrlError


# 请求jav在javdb上的网页，返回html
def get_db_html(url, proxy):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/86.0.4240.198 Safari/537.36",
        "accept-encodin": "gzip, deflate, br",
    }
    for retry in range(1, 11):
        try:
            if proxy:
                rqs = requests.get(url, header=headers, proxies=proxy, timeout=(6, 7))
            else:
                rqs = requests.get(url, headers=headers, timeout=(6, 7))
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
        # print(rqs_content)
        if re.search(r'成人影片數據庫', rqs_content):
            return rqs_content
        elif re.search(r'頁面未找到', rqs_content):
            return rqs_content
        else:
            print(rqs_content)
            print('    >打开网页失败，空返回...重新尝试...')
            continue
    input(f'>>请检查你的网络环境是否可以打开: {url}')


def scrape_from_db(jav_file, jav_model, url_db, proxy_db):
    # 用户指定了网址，则直接得到jav所在网址
    if '仓库' in jav_file.Name:
        url_appointg = re.search(r'仓库(\w+?)\.', jav_file.Name)
        if url_appointg:
            javdb = url_appointg.group(1)
            url_jav_db = f'{url_db}/v/{javdb}'
            html_jav_db = get_db_html(url_jav_db, proxy_db)
            if re.search(r'頁面未找到', html_jav_db):
                raise SpecifiedUrlError(f'你指定的javdb网址找不到jav: {url_jav_db}，')
        else:
            # 指定的javlibrary网址有错误
            raise SpecifiedUrlError(f'你指定的javdb网址有错误: ')

    # 用户没有指定网址，则去搜索
    else:   # https://javdb9.com/video_codes/PKPD
        # 当前车牌的车头、车尾
        pref_current, suf_current = jav_file.Car.split("-")
        suf_current = int(extract_number_from_car_suf(suf_current))    # 去除车尾 末尾可能存在的字母
        # 车头的第一页
        url_pref = f'{url_db}/video_codes/{pref_current}'
        html_pref = get_db_html(url_pref, proxy_db)
        # 第一页上的所有box
        list_cars = etree.HTML(html_pref).xpath('//*[@class="video-title"]/strong/text()')
        # javdb没有该车头的页面
        if not list_cars:
            return ScrapeStatusEnum.db_not_found, []
        # 第一页的末尾，即最小suf
        suf_min = int(extract_number_from_car(list_cars[-1]))
        # 预估 当前车尾 和 第一页的最小车尾 的差距，在第几页
        no_page = (suf_min - suf_current) // 40 + 2 if suf_min > suf_current else 1
        # 预估当前车牌 所在页面
        if no_page > 1:
            url_page = f'{url_db}/video_codes/{pref_current}?page={no_page}'
            html_pref = get_db_html(url_page, proxy_db)
            list_cars = etree.HTML(html_pref).xpath('//*[@class="video-title"]/strong/text()')
        # 预估的页面的最小和最大suf
        if list_cars:
            suf_min_n = int(extract_number_from_car(list_cars[-1]))
            suf_max_n = int(extract_number_from_car(list_cars[0]))
        # 预估的页面已经超出范围，比如实际只有10页，预估到12页。
        else:
            # 防止预估的no_page太大，比如HODV-21301
            if no_page > 100:
                no_page = 100
            # 往前推,直至找到最后有数据的那一页
            while True:
                no_page -= 1
                url_page = f'{url_db}/video_codes/{pref_current}?page={no_page}'
                # print(url_page)
                html_pref = get_db_html(url_page, proxy_db)
                list_cars = etree.HTML(html_pref).xpath('//*[@class="video-title"]/strong/text()')
                if list_cars:
                    # 将往前推的、第一个有数据的这一页,作为预估的页面,取最小和最大suf
                    suf_min_n = int(extract_number_from_car(list_cars[-1]))
                    suf_max_n = int(extract_number_from_car(list_cars[0]))
                    break
        # 在预估页面中
        if suf_max_n >= suf_current >= suf_min_n:
            no_target = find_javdb_code(suf_current, list_cars)
            if not no_target:
                return ScrapeStatusEnum.db_not_found, []
            javdb = etree.HTML(html_pref).xpath(f'//*[@class="item"][{no_target}]/a/@href')[0][3:]
        else:
            # 如果比 预估页面 的最小车尾 还小，页码依次往后+1；如果比 预估页面 的最大车尾 还大，页码依次往前-1
            one = 1 if suf_current < suf_min_n else -1
            while True:
                no_page += one
                if no_page == 0:
                    return ScrapeStatusEnum.db_not_found, []
                url_page_next = f'{url_db}/video_codes/{pref_current}?page={no_page}'
                html_pref_next = get_db_html(url_page_next, proxy_db)
                list_cars_next = etree.HTML(html_pref_next).xpath('//*[@class="video-title"]/strong/text()')
                # 这一页已经没有内容了
                if not list_cars_next:
                    return ScrapeStatusEnum.db_not_found, []
                # 有内容,匹配下
                no_target = find_javdb_code(suf_current, list_cars_next)
                # 找到了退出
                if no_target:
                    javdb = etree.HTML(html_pref_next).xpath(f'//*[@class="item"][{no_target}]/a/@href')[0][3:]
                    break
                # 当前车牌suf在这一首尾之间,但还是找不到,则退出
                suf_min_next = int(extract_number_from_car(list_cars_next[-1]))
                suf_max_next = int(extract_number_from_car(list_cars_next[0]))
                if suf_current in range(suf_min_next, suf_max_next + 1):
                    return ScrapeStatusEnum.db_not_found, []

    # 得到 javdb
    url_jav_db = f'{url_db}/v/{javdb}'
    print('    >前往javdb: ', url_jav_db)
    html_jav_db = get_db_html(url_jav_db, proxy_db)
    # <title> BKD-171 母子交尾 ～西会津路～ 中森いつき | JavDB 成人影片資料庫及磁鏈分享 </title>
    car_title = re.search(r'title> (.+) \| JavDB', html_jav_db).group(1)
    list_car_title = car_title.split(' ', 1)
    jav_model.Car = list_car_title[0]  # 围绕该jav的所有信息
    jav_model.Title = list_car_title[1]
    jav_model.Javdb = javdb
    # 带着主要信息的那一块 複製番號" data-clipboard-text="BKD-171">
    html_jav_db = re.search(r'複製番號([\s\S]+?)存入清單', html_jav_db, re.DOTALL).group(1)
    # 系列 "/series/RJmR">○○に欲望剥き出しでハメまくった中出し記録。</a>
    seriesg = re.search(r'series/.+?">(.+?)</a>', html_jav_db)
    jav_model.Series = seriesg.group(1) if seriesg else ''
    # 上映日 e">2019-02-01<
    releaseg = re.search(r'(\d\d\d\d-\d\d-\d\d)', html_jav_db)
    jav_model.Release = releaseg.group(1) if releaseg else '1970-01-01'
    # 片长 value">175 分鍾<
    runtimeg = re.search(r'value">(\d+) 分鍾<', html_jav_db)
    jav_model.Runtime = int(runtimeg.group(1)) if runtimeg else 0
    # 导演 /directors/WZg">NABE<
    directorg = re.search(r'directors/.+?">(.+?)<', html_jav_db)
    jav_model.Director = directorg.group(1) if directorg else ''
    # 制作商 e"><a href="/makers/
    studiog = re.search(r'makers/.+?">(.+?)<', html_jav_db)
    jav_model.Studio = studiog.group(1) if studiog else ''
    # 发行商 /publishers/pkAb">AV OPEN 2018</a><
    publisherg = re.search(r'publishers.+?">(.+?)</a><', html_jav_db)
    jav_model.Publisher = publisherg.group(1) if publisherg else ''
    # 评分 star gray"></i></span>&nbsp;3.75分
    scoreg = re.search(r'star gray"></i></span>&nbsp;(.+?)分', html_jav_db)
    jav_model.Score = int(float(scoreg.group(1)) * 20) if scoreg else 0
    # 演员们 /actors/M0xA">上川星空</a>  actors/P9mN">希美まゆ</a><strong class="symbol female
    actors = re.findall(r'actors/.+?">(.+?)</a><strong class="symbol female', html_jav_db)
    jav_model.Actors = [i.strip() for i in actors]
    str_actors = ' '.join(jav_model.Actors)
    # 去除末尾的标题 javdb上的演员不像javlibrary使用演员最熟知的名字
    if str_actors and jav_model.Title.endswith(str_actors):
        jav_model.Title = jav_model.Title[:-len(str_actors)].strip()
    # print('    >演员: ', actors)
    # 特征 /tags?c7=8">精选、综合</a>
    genres_db = re.findall(r'tags.+?">(.+?)</a>', html_jav_db)
    return ScrapeStatusEnum.success, genres_db


def find_javdb_code(suf_current, list_cars):
    for i, suf_str in enumerate(list_cars):
        if int(extract_number_from_car(suf_str)) == suf_current:
            return i + 1    # 第几个，在list的下标基础上+1
    return ''
