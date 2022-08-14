from time import strftime, localtime, time


class Logger(object):
    def __init__(self):
        self.no_fail = 0  # 数量: 已经或可能导致致命错误，比如整理未完成，同车牌有不同视频
        self.no_warn = 0  # 数量: 对整理结果不致命的问题，比如找不到简介
        self.path_relative = ''   # 当前jav_file的相对dir_choose的路径，用于记错

    def rest(self):
        self.no_fail = 0
        self.no_warn = 0

    # 功能: print错误信息并写入日志
    # 参数: 错误信息
    # 返回: 无
    # 辅助: 无
    def record_fail(self, fail_msg, extra_msg=None):
        self.no_fail += 1
        # python 如何让类方法获取实例属性作为参数的默认值？暂时没有
        if not extra_msg:
            extra_msg = self.path_relative
        msg = f'    >第{self.no_fail}个失败！{fail_msg}{extra_msg}\n'
        txt = open('【可删除】失败记录.txt', 'a', encoding="utf-8")
        txt.write(msg)
        txt.close()
        print(msg, end='')

    # 功能: print警告信息并写入日志
    # 参数: 警告信息
    # 返回: 无
    # 辅助: 无
    def record_warn(self, warn_msg, extra_msg=None):
        self.no_warn += 1
        if not extra_msg:
            extra_msg = self.path_relative
        msg = f'    >第{self.no_warn}个警告！{warn_msg}{extra_msg}\n'
        txt = open('【可删除】警告信息.txt', 'a', encoding="utf-8")
        txt.write(msg)
        txt.close()
        print(msg, end='')

    # 功能: 记录整理的文件夹、整理的时间
    # 参数: 错误信息
    # 返回: 无
    # 辅助: os.strftime, os.localtime, os.time,
    @staticmethod
    def record_start(dir_choose):
        msg = f'已选择文件夹: {dir_choose}  {strftime("%Y-%m-%d %H:%M:%S", localtime(time()))}\n'
        txt = open('【可删除】失败记录.txt', 'a', encoding="utf-8")
        txt.write(msg)
        txt.close()
        txt = open('【可删除】警告信息.txt', 'a', encoding="utf-8")
        txt.write(msg)
        txt.close()
        txt = open('【可删除】新旧文件名清单.txt', 'a', encoding="utf-8")
        txt.write(msg)
        txt.close()

    def print_end(self, dir_choose):
        if self.no_fail > 0:
            print('失败', self.no_fail, '个!  ', dir_choose, '\n')
            line = -1
            with open('【可删除】失败记录.txt', 'r', encoding="utf-8") as f:
                content = list(f)
            while 1:
                if content[line].startswith('已'):
                    break
                line -= 1
            for i in range(line + 1, 0):
                print(content[i], end='')
            print('\n“【可删除】失败记录.txt”已记录错误\n')
        else:
            print(' “0”失败！  ', dir_choose, '\n')
        if self.no_warn > 0:
            print('“警告信息.txt”还记录了', self.no_warn, '个警告信息！\n')


# 功能: 记录旧文件名
# 参数: 新文件名，旧文件名
# 返回: 无
# 辅助: 无
def record_video_old(name_new, name_old):
    txt = open('【可删除】新旧文件名清单.txt', 'a', encoding="utf-8")
    txt.write(f'<<<< {name_old}\n')
    txt.write(f'>>>> {name_new}\n')
    txt.close()
