# -*- coding:utf-8 -*-
import re


# 功能: 发现原视频文件名中用于javbus的有码车牌
# 参数: 大写后的视频文件名，素人车牌list_suren_car    示例: AVOP-127.MP4    ['LUXU', 'MIUM']
# 返回: 发现的车牌    示例: AVOP-127
# 辅助: re.search
def find_car_youma(file, list_suren_car):
    # car_pref 车牌前缀 ABP-，带横杠；car_suf，车牌后缀 123。
    # 先处理特例 T28 车牌
    if re.search(r'[^A-Z]?T28[-_ ]*\d\d+', file):
        car_pref = 'T28-'
        car_suf = re.search(r'T28[-_ ]*(\d\d+)', file).group(1)
    # 以javbus上记录的20ID-020为标准
    elif re.search(r'[^\d]?\d\dID[-_ ]*\d\d+', file):
        carg = re.search(r'(\d\d)ID[-_ ]*(\d\d+)', file)
        car_pref = 'ID-'
        car_suf = f'{carg.group(1)}{carg.group(2)}'
    # 一般车牌
    elif re.search(r'[A-Z]+[-_ ]*\d\d+', file):
        carg = re.search(r'([A-Z]+)[-_ ]*(\d\d+)', file)
        car_pref = carg.group(1)
        if car_pref in list_suren_car or car_pref in ['HEYZO', 'PONDO', 'CARIB', 'OKYOHOT']:
            return ''
        car_pref = f'{car_pref}-'
        car_suf = carg.group(2)
    else:
        return ''
    # 去掉太多的0，avop00127 => avop-127
    if len(car_suf) > 3:
        car_suf = f'{car_suf[:-3].lstrip("0")}{car_suf[-3:]}'
    return f'{car_pref}{car_suf}'


# 功能: 发现原视频文件名中的无码车牌
# 参数: 被大写后的视频文件名，素人车牌list_suren_car    示例: ABC123ABC123.MP4    ['LUXU', 'MIUM']
# 返回: 发现的车牌    示例: ABC123ABC123，只要是字母数字，全拿着
# 辅助: re.search
def find_car_wuma(file, list_suren_car):
    # N12345
    if re.search(r'[^A-Z]?N\d\d+', file):
        car_pref = 'N'
        car_suf = re.search(r'N(\d\d+)', file).group(1)
    # 123-12345
    elif re.search(r'\d+[-_ ]\d\d+', file):
        carg = re.search(r'(\d+)[-_ ](\d\d+)', file)
        car_pref = f'{carg.group(1)}-'
        car_suf = carg.group(2)
    # 只要是字母数字-_，全拿着
    elif re.search(r'[A-Z0-9]+[-_ ]?[A-Z0-9]+', file):
        carg = re.search(r'([A-Z0-9]+)([-_ ]*)([A-Z0-9]+)', file)
        car_pref = carg.group(1)
        # print(car_pref)
        if car_pref in list_suren_car:
            return ''
        car_pref = f'{car_pref}{carg.group(2)}'
        car_suf = carg.group(3)
    # 下面是处理和一般有码车牌差不多的无码车牌，拿到的往往是错误的，仅在1.0.4版本使用过，宁可不整理也不识别个错的
    # elif search(r'[A-Z]+[-_ ]?\d+', file):
    #     carg = search(r'([A-Z]+)([-_ ]?)(\d+)', file)
    #     car_pref = carg.group(1)
    #     if car_pref in list_suren_car:
    #         return ''
    #     car_pref = f'{car_pref}{carg.group(2)}'
    #     car_suf = carg.group(3)
    else:
        return ''
    # 无码就不去0了，去了0和不去0，可能是不同结果
    # if len(car_suf) > 3:
    #     car_suf = f'{car_suf[:-3].lstrip("0")}{car_suf[-3:]}'
    return f'{car_pref}{car_suf}'


# 功能: 发现素人车牌，直接从已记录的list_suren_car中来对比
# 参数: 大写后的视频文件名，素人车牌list_suren_car    示例: LUXU-123.MP4    ['LUXU', 'MIUM']
# 返回: 发现的车牌    示例: LUXU-123
# 辅助: re.search
def find_car_suren(file, list_suren_car):
    carg = re.search(r'([A-Z][A-Z]+)[-_ ]*(\d\d+)', file)  # 匹配字幕车牌
    if carg:
        car_pref = carg.group(1)
        # 如果用户把视频文件名指定为jav321上的网址，让该视频通过
        if car_pref not in list_suren_car and '三二一' not in file:
            return ''
        car_suf = carg.group(2)
        # 去掉太多的0，avop00127
        if len(car_suf) > 3:
            car_suf = f'{car_suf[:-3].lstrip("0")}{car_suf[-3:]}'
        return f'{car_pref}-{car_suf}'
    else:
        return ''


def find_car_fc2(file):
    subtitle_carg = re.search(r'FC2[^\d]*(\d+)', file)  # 匹配字幕车牌
    subtitle_car = f'FC2-{subtitle_carg.group(1)}' if subtitle_carg else ''
    return subtitle_car


def extract_number_from_car_suf(suf):
    # print(type(suf))
    return re.search(r'(\d+)\w*', suf).group(1)


def extract_number_from_car(car):
    if '-' in car:
        return re.search(r'-(\d+)\w*', car).group(1)
    else:
        return re.search(r'(\d+)\w*', car).group(1)
