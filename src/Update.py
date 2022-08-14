# -*- coding:utf-8 -*-
import requests, re, os

now_version = '1.1.4'
print('当前版本为: ', now_version)
print('正在检查更新...https://github.com/junerain123/javsdt/blob/master/%E6%A3%80%E6%9F%A5%E6%9B%B4%E6%96%B0.json')
upd_url = 'https://github.com/junerain123/javsdt/blob/master/%E6%A3%80%E6%9F%A5%E6%9B%B4%E6%96%B0.json'
try:
    rqs = requests.get(upd_url, timeout=20)
except:
    input('连接github超时！请重新尝试！')
rqs.encoding = 'utf-8'
html_github_update = rqs.text
# print(html_github_update)
version_g = re.search(r'version<span class="pl-pds">&quot;</span></span>: <span class="pl-s"><span class="pl-pds">&quot;</span>(.+?)<', html_github_update)
new_version = version_g.group(1)
download_g = re.search(r'lanzous.com/(.+?)<', html_github_update)
new_download = 'https://www.lanzous.com/' + download_g.group(1)
print('最新版本为:', new_version)
if now_version != new_version:
    print('请下载最新的版本: ', new_version, '！')
    print('下载链接为: ', new_download, '！')
else:
    print('你正在使用最新的版本，无需更新！')
input("结束！")
