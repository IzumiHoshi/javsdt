# -*- coding:utf-8 -*-
import requests
import json
from time import sleep, time
from hashlib import md5
# from traceback import format_exc


# 功能: 调用百度翻译API接口，翻译日语简介
# 参数: 百度翻译api账户api_id, api_key，需要翻译的内容word，目标语言to_lang
# 返回: 中文简介string
# 辅助: os.system, hashlib.md5，time.time，requests.get，json.loads
def translate(api_id, api_key, word, to_lang):
    if not word:
        return ''
    if not api_id or not api_key:
        print('    >你没有正确填写百度翻译api账户!!!')
        return ''
    for retry in range(10):
        # 把账户、翻译的内容、时间 混合md5加密，传给百度验证
        salt = str(time())[:10]
        final_sign = f'{api_id}{word}{salt}{api_key}'
        final_sign = md5(final_sign.encode("utf-8")).hexdigest()
        # 表单paramas
        paramas = {
            'q': word,
            'from': 'jp',
            'to': to_lang,
            'appid': '%s' % api_id,
            'salt': '%s' % salt,
            'sign': '%s' % final_sign
        }
        try:
            response = requests.get('http://api.fanyi.baidu.com/api/trans/vip/translate',
                                    params=paramas, timeout=(6, 7))
        except:
            print('    >百度翻译拉闸了...重新翻译...')
            continue
        content = str(response.content, encoding="utf-8")
        # 百度返回为空
        if not content:
            print('    >百度翻译返回为空...重新翻译...')
            sleep(1)
            continue
        # 百度返回了dict json
        json_reads = json.loads(content)
        # print(json_reads)
        if 'error_code' in json_reads:    # 返回错误码
            error_code = json_reads['error_code']
            if error_code == '54003':
                print('    >请求百度翻译太快...技能冷却1秒...')
                sleep(1)
            elif error_code == '54005':
                print('    >发送了太多超长的简介给百度翻译...技能冷却3秒...')
                sleep(3)
            elif error_code == '52001':
                print('    >连接百度翻译超时...重新翻译...')
            elif error_code == '52002':
                print('    >百度翻译拉闸了...重新翻译...')
            elif error_code == '54003':
                print('    >使用过于频繁，百度翻译不想给你用了...')
            elif error_code == '52003':
                print('    >请正确输入百度翻译API账号，请阅读【使用说明】！')
                input('>>javsdt已停止工作...')
            elif error_code == '58003':
                print('    >你的百度翻译API账户被百度封禁了，请联系作者，告诉你解封办法！“')
                input('>>javsdt已停止工作...')
            elif error_code == '90107':
                print('    >你的百度翻译API账户还未通过认证或者失效，请前往API控制台解决问题！“')
                input('>>javsdt已停止工作...')
            else:
                print('    >百度翻译error_code！请截图联系作者！', error_code)
            continue
        else:  # 返回正确信息
            return json_reads['trans_result'][0]['dst']
    print('    >翻译简介失败...请截图联系作者...')
    return f'【百度翻译出错】{word}'
