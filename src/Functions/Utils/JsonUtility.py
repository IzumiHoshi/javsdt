# -*- coding:utf-8 -*-
import os
from json import load


def read_json_to_dict(path):
    f = open(path, encoding='utf-8')
    dict_json = load(f)
    f.close()
    return dict_json


# 显示某一路径json的内容
def show_json_by_path(path):
    dict_json = read_json_to_dict(path)
    for i in dict_json:
        print(i, ':', dict_json[i])


# 展示所有json中的某一项，某一项由手动输入
def show_jsons_one_element_by_dir_choose(dir_choose, key):
    for root, dirs, files in os.walk(dir_choose):
        for file in files:
            if file.endswith(('.json',)):
                path = f'{root}\\{file}'
                dict_json = read_json_to_dict(path)
                print(dict_json['Car'], dict_json[key])


# 展示所有json中的某一项，某一项由手动输入
def show_json_one_element_by_path(path, key):
    dict_json = read_json_to_dict(path)
    try:
        print(dict_json[key])
    except KeyError:
        print('无')


# 检查某一路径的json是否没有“剧情”
def check_lost_plot(path):
    if os.path.exists(path):
        dict_json = read_json_to_dict(path)
        # print('当前plot如下')
        # print('plot:', dict_json['plot'])
        if dict_json['plot'] == '未知简介':
            return True
        else:
            return False
    else:
        print('  >没有json：', path)
        return False


# 检查某一路径的json是否没有 系列
def check_lost_series(path):
    if os.path.exists(path):
        dict_json = read_json_to_dict(path)
        if dict_json['series'] == '未知系列':
            return True
        else:
            return False
    else:
        print('  >没有json：', path)
        return False


def judge_json_contain_one_genre_by_path(path, genre):
    dict_json = read_json_to_dict(path)
    print('正在检查: ', path)
    if genre in dict_json['Genres']:
        print(path, dict_json['Genres'])
        return True
    else:
        return False
