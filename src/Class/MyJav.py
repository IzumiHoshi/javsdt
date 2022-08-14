# -*- coding:utf-8 -*-
import time
from os.path import splitext, basename
from os import sep

from Class.MyEnum import CompletionStatusEnum, CutTypeEnum


# 每一部jav的“结构体”
class JavFile(object):
    def __init__(self, car, car_id, file_raw, dir_current, episode, subtitle, no_current):
        self.Car = car                                     # 车牌
        self.Car_id = car_id                               # 去bus和arzon搜索的车牌，不同在于Car_id是26ID-xxx，Car是ID-26xxx
        self.Pref = car.split('-')[0]                      # 车牌前缀
        self.Name = file_raw                               # 完整文件名 ABC-123-cd2.mp4；会在重命名过程中发生变化
        self.Ext = splitext(file_raw)[1].lower()           # 视频文件扩展名 .mp4
        self.Dir = dir_current                             # 视频所在文件夹的路径；会在重命名过程中发生变化
        self.Episode = episode                             # 第几集 cd1 cd2 cd3
        self.Sum_all_episodes = 0                          # 当前车牌总共多少集，用户的
        self.Subtitle = subtitle                           # 字幕文件名  ABC-123.srt；会在重命名过程中发生变化
        self.Ext_subtitle = splitext(subtitle)[1].lower()  # 字幕扩展名  .srt
        self.No = no_current                              # 当前处理的视频在所有视频中的编号，整理进度
        self.Bool_subtitle = False                           # 拥有字幕
        self.Bool_divulge = False                            # 是无码流出

    # 类属性，类似于面向对象语言中的静态成员
    Bool_in_separate_folder = False         # 是否拥有独立文件夹

    # 多cd，如果有两集，第一集cd1.第二集cd2；如果只有一集，为空
    @property
    def Cd(self):
        return f'-cd{self.Episode}' if self.Sum_all_episodes > 1 else ''

    # 所在文件夹名称
    @property
    def Folder(self):
        return basename(self.Dir)

    # 这下面列为属性而不是字段，因为name、dir、subtitle会发生变化
    # 视频文件完整路径
    @property
    def Path(self):
        return f'{self.Dir}{sep}{self.Name}'

    # 视频文件名，但不带文件扩展名
    @property
    def Name_no_ext(self):
        return splitext(self.Name)[0]

    # 字幕文件完整路径
    @property
    def Path_subtitle(self):
        return f'{self.Dir}{sep}{self.Subtitle}'


class JavModel(object):
    def __init__(self, **entries):
        self.Car = ''                # 1 车牌
        self.CarOrigin = ''           # 2 原始车牌
        self.Series = ''              # 3 系列
        self.Title = ''               # 4 原标题
        self.TitleZh = ''             # 5 简体中文标题
        self.Plot = ''                # 6 剧情概述
        self.PlotZh = ''              # 7 简体剧情
        self.Review = ''              # 8 剧评
        self.Release = '1970-01-01'   # 9 发行日期
        self.Runtime = 0              # 10 时长
        self.Director = ''            # 11 导演
        self.Studio = ''              # 12 制造商
        self.Publisher = ''           # 13 发行商
        self.Score = 0                # 14 评分
        self.CoverLibrary = ''        # 15 封面Library
        self.CoverBus = ''            # 16 封面Bus
        self.CutType = CutTypeEnum.left.value    # 17 裁剪方式
        self.Javdb = ''               # 18 db编号
        self.Javlibrary = ''          # 19 library编号
        self.Javbus = ''              # 20 bus编号
        self.Arzon = ''               # 21 arzon编号
        self.CompletionStatus = CompletionStatusEnum.unknown.value    # 22 完成度，三大网站为全部
        self.Version = 1              # 23 版本
        self.Genres = []              # 24 类型
        self.Actors = []              # 25 演员们
        self.Modify = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.__dict__.update(entries)

    def prefect_completion_status(self):
        if self.Javdb:
            if self.Javlibrary:
                if self.Javbus:
                    completion = CompletionStatusEnum.db_library_bus.value
                else:
                    completion = CompletionStatusEnum.db_library.value
            else:
                if self.Javbus:
                    completion = CompletionStatusEnum.db_bus.value
                else:
                    completion = CompletionStatusEnum.only_db.value
        else:
            if self.Javlibrary:
                if self.Javbus:
                    completion = CompletionStatusEnum.library_bus.value
                else:
                    completion = CompletionStatusEnum.only_library.value
            else:
                if self.Javbus:
                    completion = CompletionStatusEnum.only_bus.value
                else:
                    completion = CompletionStatusEnum.unknown.value
        self.CompletionStatus = completion
