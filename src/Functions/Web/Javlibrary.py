# -*- coding:utf-8 -*-
import re
import requests
from Class.MyEnum import ScrapeStatusEnum
from Class.MyError import SpecifiedUrlError
from Functions.Utils.XML import replace_xml_win
# from traceback import format_exc


# 搜索javlibrary，或请求javlibrary上jav所在网页，返回html
def get_library_html(url, proxy):
    for retry in range(10):
        try:
            if proxy:
                rqs = requests.get(url, proxies=proxy, timeout=(6, 7))
            else:
                rqs = requests.get(url, timeout=(6, 7))
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
        if re.search(r'JAVLibrary', rqs_content):        # 得到想要的网页，直接返回
            return rqs_content
        else:                                         # 代理工具返回的错误信息
            print('    >打开网页失败，空返回...重新尝试...')
            continue
    input(f'>>请检查你的网络环境是否可以打开: {url}')


# 返回: Status, html_jav_library
def scrape_from_library(jav_file, jav_model, url_library, proxy_library):
    status = ScrapeStatusEnum.success
    # 用户指定了网址，则直接得到jav所在网址
    if '图书馆' in jav_file.Name:
        url_appointg = re.search(r'图书馆(jav.+?)\.', jav_file.Name)
        if url_appointg:
            url_jav_library = f'{url_library}/?v={url_appointg.group(1)}'
            print(f'    >指定网址: {url_jav_library}')
            html_jav_library = get_library_html(url_jav_library, proxy_library)
            titleg = re.search(r'<title>([A-Z].+?) - JAVLibrary</title>', html_jav_library)  # 匹配处理“标题”
            if not titleg:
                raise SpecifiedUrlError(f'你指定的javlibrary网址找不到jav: {url_jav_library}，')
        else:
            # 指定的javlibrary网址有错误
            raise SpecifiedUrlError(f'你指定的javlibrary网址有错误: ')
    # 用户没有指定网址，则去搜索
    else:
        url_search = f'{url_library}/vl_searchbyid.php?keyword={jav_file.Car}'
        print(f'    >搜索javlibrary: {url_search}')
        # 得到javlibrary搜索网页html
        html_search_library = get_library_html(url_search, proxy_library)
        # 从前: 搜索结果，大部分情况就是这个影片的网页（搜索结果唯一，javlibrary会自动跳转到该jav唯一的网页），另一种情况是多个搜索结果的网页 目前版本请无视这一行:
        # 访问javlibrary需要cloudflare的通行证，自动跳转时，cookie会发生变化，导致用现有cookie无权访问跳转后的页面。所以现在程序不希望requests
        # 帮助自动跳转，而是只得到跳转前网页上的线索，再自行访问这个跳转目标网页。 尝试找标题，第一种情况: 找得到，就是这个影片的网页。
        titleg = re.search(r'<title>([A-Z].+?) - JAVLibrary</title>', html_search_library)  # 匹配处理“标题”
        # 搜索结果就是AV的页面。事实上，现在只有用户指定了网址，这一步判定才能成功。现在要么是多个搜索结果的网页，要么是跳转前的几句html语句，根本不可能“搜索一下就是AV的页面”。
        if titleg:
            html_jav_library = html_search_library
        # 第二种情况: 搜索结果可能是两个以上，所以这种匹配找不到标题，None！
        else:  # 找“可能是多个结果的网页”上的所有“box”
            # 这个正则表达式可以忽略avop-00127bod，它是近几年重置的，信息冗余
            list_search_results = re.findall(r'v=jav(.+?)" title="(.+?-\d+?[a-z]? .+?)"', html_search_library)
            # print(list_search_results)
            # 从这些搜索结果中，找到最正确的一个
            if list_search_results:
                # 默认用第一个搜索结果
                url_jav = f'{url_library}/?v=jav{list_search_results[0][0]}'
                # 在javlibrary上搜索 SSNI-589 SNIS-459 这两个车牌，你就能看懂下面的if
                if len(list_search_results) > 1 and not list_search_results[1][1].endswith('ク）'):  # ク）是蓝光重置版
                    # print(list_search_results)
                    # 排在第一个的是蓝光重置版，比如SSNI-589（ブルーレイディスク），它的封面不正常，跳过它
                    if list_search_results[0][1].endswith('ク）'):
                        url_jav = f'{url_library}/?v=jav{list_search_results[1][0]}'
                    # 不同的片，但车牌完全相同，比如id-020。警告用户，但默认用第一个结果。
                    elif list_search_results[1][1].split(' ', 1)[0] == jav_file.Car:
                        # 搜索到同车牌的不同视频
                        status = ScrapeStatusEnum.library_multiple_search_results
                    # else: 还有一种情况，不同片，车牌也不同，但搜索到一堆，比如搜“AVOP-039”，还会得到“AVOP-390”，正确的肯定是第一个。
                # 打开这个jav在library上的网页
                print(f'    >获取信息: {url_jav}')
                html_jav_library = get_library_html(url_jav, proxy_library)
            # 第三种情况: 搜索不到这部影片，搜索结果页面什么都没有
            else:
                return ScrapeStatusEnum.library_not_found, []
    # 标题
    if not jav_model.Title:
        jav_model.Title = re.search(r'<title>([A-Z].+?) - JAVLibrary</title>', html_jav_library).group(1)
    if not jav_model.Car:
        car_titleg = re.search(r'(.+?) (.+)', jav_model.Title)
        # 车牌号
        car_temp = car_titleg.group(1)
        # 在javlibrary中，T-28 和 ID 的车牌很奇特。javlibrary是T-28XXX，而其他网站是T28-XXX；ID-20XXX，而其他网站是20ID-XXX。
        if 'T-28' in car_temp:
            car_temp = car_temp.replace('T-28', 'T28-', 1)
        # elif 'ID-' in car_temp:
        #     jav_tempg = re.search(r'ID-(\d\d)(\d\d\d)', car_temp)
        #     if jav_tempg:
        #         car_temp = jav_tempg.group(1) + 'ID-' + jav_tempg.group(2)
        jav_model.Car = car_temp
    # javlibrary的精彩影评   (.+?\s*.*?\s*.*?\s*.*?) 下面的匹配可能很奇怪，没办法，就这么奇怪
    review = ''
    list_all_reviews = re.findall(
        r'(textarea style="display: none;" class="hidden">[\s\S]*?scoreup">\d\d+)', html_jav_library, re.DOTALL)
    if list_all_reviews:
        for rev in list_all_reviews:
            list_reviews = re.findall(r'hidden">([\s\S]*?)</textarea>', rev, re.DOTALL)
            if list_reviews:
                review = f'{review}//{list_reviews[-1]}//'
        review = review.replace('\n', '').replace('\t', '').replace('\r', '').strip()
    if review:
        review = f'//{review}'
    jav_model.Review = review
    # print(review)
    # 有大部分信息的html_jav_library
    html_jav_library = re.search(r'video_title"([\s\S]*?)favorite_edit', html_jav_library, re.DOTALL).group(1)
    # href="/cn/?v=javmeza25m"
    jav_model.Javlibrary = re.search(r'href="/cn/\?v=(.+?)"', html_jav_library).group(1)
    # DVD封面cover
    coverg = re.search(r'src="(.+?)" width="600', html_jav_library)
    if coverg:
        cover_library = coverg.group(1)
        if not cover_library.startswith('http'):
            cover_library = f'http:{cover_library}'
        jav_model.CoverLibrary = cover_library
        jav_model.CarOrigin = cover_library.split('/')[-2]
    # 发行日期
    if jav_model.Release == '1970-01-01':
        premieredg = re.search(r'(\d\d\d\d-\d\d-\d\d)', html_jav_library)
        jav_model.Release = premieredg.group(1) if premieredg else '1970-01-01'
    # 片长 <td><span class="text">150</span> 分钟</td>
    if jav_model.Runtime == 0:
        runtimeg = re.search(r'span class="text">(\d+?)</span>', html_jav_library)
        jav_model.Runtime = runtimeg.group(1) if runtimeg else 0
    # 导演
    if not jav_model.Director:
        directorg = re.search(r'director\.php.+?>(.+?)<', html_jav_library)
        jav_model.Director = replace_xml_win(directorg.group(1)) if directorg else ''
    # 制作商
    if not jav_model.Studio:
        studiog = re.search(r'maker\.php.+?>(.+?)<', html_jav_library)
        jav_model.Studio = replace_xml_win(studiog.group(1)) if studiog else ''
    # 发行商
    if not jav_model.Publisher:
        publisherg = re.search(r'rel="tag">(.+?)</a> &nbsp;<span id="label_', html_jav_library)
        jav_model.Publisher = publisherg.group(1) if publisherg else ''
    # 演员们
    actors = re.findall(r'star\.php.+?>(.+?)<', html_jav_library)
    if actors:
        jav_model.Actors = actors
        # 去除末尾的标题 javdb上的演员不像javlibrary使用演员最熟知的名字
        str_actors = ' '.join(jav_model.Actors)
        if str_actors and jav_model.Title.endswith(str_actors):
            jav_model.Title = jav_model.Title[:-len(str_actors)].strip()
    # 评分
    if jav_model.Score == 0:
        scoreg = re.search(r'score">\((.+?)\)<', html_jav_library)
        if scoreg:
            jav_model.Score = int(float(scoreg.group(1)) * 10)
    # 特点风格
    genres_library = re.findall(r'category tag">(.+?)<', html_jav_library)
    return status, genres_library
