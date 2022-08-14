# -*- coding:utf-8 -*-


# 功能: 去除xml文档不允许的特殊字符 &<>
# 参数: （文件名、简介、标题）str
# 返回: str
# 辅助: 无
def replace_xml(name):
    # 替换xml中的不允许的特殊字符 .replace('\'', '&apos;').replace('\"', '&quot;')
    # .replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')  nfo基于xml，xml中不允许这5个字符，但实际测试nfo只不允许左边3个
    return name.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')\
                .replace('\n', '').replace('\t', '').replace('\r', '').strip()


# 功能: 去除xml文档和windows路径不允许的特殊字符 &<>  \/:*?"<>|
# 参数: （文件名、简介、标题）str
# 返回: str
# 辅助: 无
def replace_xml_win(name):
    # 替换windows路径不允许的特殊字符 \/:*?"<>|
    return name.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')\
                .replace('\n', '').replace('\t', '').replace('\r', '')\
                .replace("\\", "#").replace("/", "#").replace(":", "：").replace("*", "#")\
                .replace("?", "？").replace("\"", "#").replace("|", "#").strip()
