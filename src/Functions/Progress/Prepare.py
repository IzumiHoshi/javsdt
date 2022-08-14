from configparser import RawConfigParser


def write_new_arzon_phpsessid(phpsessid):
    config_settings = RawConfigParser()
    config_settings.read('【点我设置整理规则】.ini', encoding='utf-8-sig')
    config_settings.set("其他设置", "arzon的phpsessid", phpsessid)
    config_settings.write(open('【点我设置整理规则】.ini', "w", encoding='utf-8-sig'))
    print('    >保存新的arzon的phpsessid至【点我设置整理规则】.ini成功！')


# 功能: 得到素人车牌集合
# 参数: 无
# 返回: 素人车牌list
# 辅助: 无
def get_suren_cars():
    try:
        with open('StaticFiles/【素人车牌】.txt', 'r', encoding="utf-8") as f:
            list_suren_cars = list(f)
    except:
        input('【素人车牌】.txt读取失败！')
    list_suren_cars = [i.strip().upper() for i in list_suren_cars if i != '\n']
    # print(list_suren_cars)
    return list_suren_cars
