# -*- coding:utf-8 -*-
import requests, os
from configparser import RawConfigParser
from base64 import b64encode
from traceback import format_exc
from json import loads
from os.path import exists

# 检查“演员头像”文件夹是否就绪
if not exists('演员头像'):
    input('\n“演员头像”文件夹丢失！请把它放进exe的文件夹中！\n')
# 读取配置文件，这个ini文件用来给用户设置emby网址和api id
print('正在读取ini中的设置...')
config_settings = RawConfigParser()
try:
    config_settings.read('【点我设置整理规则】.ini', encoding='utf-8-sig')
    url_emby = config_settings.get("emby/jellyfin", "网址")
    api_key = config_settings.get("emby/jellyfin", "api id")
    bool_replace = True if config_settings.get("emby/jellyfin", "是否覆盖以前上传的头像？") == '是' else False
except:
    url_emby = api_key = ''
    bool_replace = False
    print(format_exc())
    input('无法读取ini文件，请修改它为正确格式，或者打开“【ini】重新创建ini.exe”创建全新的ini！')
print('读取ini文件成功!\n')
# 修正用户输入的emby网址，无论是不是带“/”
url_emby = url_emby.strip('/')
# 成功的个数
num_suc = 0
num_fail = 0
num_exist = 0
sep = os.sep
try:
    print('正在获取取emby中Persons清单...')
    # curl -X GET "http://localhost:8096/emby/Persons?api_key=3291434710e342089565ad05b6b2f499" -H "accept: application/json"
    # 得到所有“人员” emby api没有细分“演员”还是“导演”“编剧”等等 下面得到的是所有“有关人员”
    url_emby_persons = f'{url_emby}/emby/Persons?api_key={api_key}'  # &PersonTypes=Actor
    try:
        rqs_emby = requests.get(url=url_emby_persons)
    except requests.exceptions.ConnectionError:
        input(f'无法访问emby服务端，请检查: {url_emby}\n')
    except:
        print(format_exc())
        input(f'发生未知错误，请截图并联系作者: {url_emby}\n')
    # 401，无权访问
    if rqs_emby.status_code == 401:
        input('请检查api id是否正确！\n')
    # print(rqs_emby.text)
    try:
        list_persons = loads(rqs_emby.text)['Items']
    except:
        list_persons = []
        print(rqs_emby.text)
        print('发生错误！emby返回内容如上: ')
        input('请截图并联系作者！')
    num_persons = len(list_persons)
    print(f'当前有{num_persons}个Person！\n')
    # 用户emby中的persons，在“演员头像”文件夹中，已有头像的，记录下来
    f_txt = open("已收录的人员清单.txt", 'w', encoding="utf-8")
    f_txt.close()
    f_txt = open("未收录的人员清单.txt", 'w', encoding="utf-8")
    f_txt.close()
    for dic_each_actor in list_persons:
        actor_name = dic_each_actor['Name']
        # 头像jpg/png在“演员头像”中的路径
        actor_pic_path = f'演员头像{sep}{actor_name[0]}{sep}{actor_name}'
        if exists(f'{actor_pic_path}.jpg'):
            actor_pic_path = f'{actor_pic_path}.jpg'
            header = {"Content-Type": 'image/jpeg', }
        elif exists(f'{actor_pic_path}.png'):
            actor_pic_path = f'{actor_pic_path}.png'
            header = {"Content-Type": 'image/png', }
        else:
            print('>>暂无头像: ', actor_name)
            f_txt = open("未收录的人员清单.txt", 'a', encoding="utf-8")
            f_txt.write(f'{actor_name}\n')
            f_txt.close()
            num_fail += 1
            continue
        # emby有某个演员，“演员头像”文件夹也有这个演员的头像，记录一下
        f_txt = open("已收录的人员清单.txt", 'a', encoding="utf-8")
        f_txt.write(f'{actor_name}\n')
        f_txt.close()
        # emby有某个演员，已经有他的头像，不再进行下面“上传头像”的操作
        if dic_each_actor['ImageTags']:  # emby已经收录头像
            num_exist += 1
            if not bool_replace:  # 不需要覆盖已有头像
                continue          # 那么不进行下面的上传操作
        f_pic = open(actor_pic_path, 'rb')  # 二进制方式打开图文件
        b6_pic = b64encode(f_pic.read())  # 读取文件内容，转换为base64编码
        f_pic.close()
        url_post_img = f'{url_emby}/emby/Items/{dic_each_actor["Id"]}/Images/Primary?api_key={api_key}'
        requests.post(url=url_post_img, data=b6_pic, headers=header)
        print('>>设置成功: ', actor_name)
        num_suc += 1

    print('\nemby/jellyfin拥有人员', num_persons, '个！')
    print('已有头像', num_exist, '个！')
    if bool_replace:
        print('当前模式: 覆盖以前上传的头像')
    else:
        print('当前模式: 跳过以前上传的头像')
    print('成功上传', num_suc, '个！')
    print('暂无头像', num_fail, '个！')
    input('已保存至“未收录的人员清单.txt”\n')
except:
    print(format_exc())
    print('发生错误！emby返回内容如上: ')
    input('请截图并联系作者！')


