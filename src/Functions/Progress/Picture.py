# -*- coding:utf-8 -*-
from PIL import Image


# 功能: 查看图片是否存在，能否打开，有没有损坏
# 参数: 图片路径path_picture
# 返回: True
# 辅助: Image.open
def check_picture(path_picture):
    try:
        img = Image.open(path_picture)
        img.load()
        return True
    except (FileNotFoundError, OSError):
        # print('文件损坏')
        return False


# 功能: 调用百度AL人体分析，分析图片中的人体
# 参数: 图片路径，百度人体分析client
# 返回: 鼻子的x坐标
# 辅助: cli.bodyAnalysis
def image_cut(path, client):
    # if bool_face:   # 启动人体分析的这两行代码在settings.py中
    #     client = AipBodyAnalysis(al_id, ai_ak, al_sk)
    for retry in range(10):
        with open(path, 'rb') as fp:
            image = fp.read()
        try:
            result = client.bodyAnalysis(image)
            return int(result["person_info"][0]['body_parts']['nose']['x'])
        except:
            print('    >人体分析出现错误，请对照“人体分析错误表格”: ', result)
            print('    >正在尝试重新人体检测...')
            continue
    input('    >人体分析无法使用...请先解决人体分析的问题，或截图联系作者...')


# 功能: 裁剪有码的fanart封面作为poster，一般fanart是800*538，把右边的379*538裁剪下来
# 参数: 已下载的fanart路径，目标poster路径
# 返回: 无
# 辅助: Image.open
def crop_poster_youma(path_fanart, path_poster):
    img = Image.open(path_fanart)
    wf, hf = img.size  # fanart的宽 高
    wide = int(hf / 1.42)  # 理想中海报的宽(应该是379)，应该是fanart的高/1.42，1.42来源于(538/379)
    # 如果fanart不是正常的800*576的横向图，而是非常“瘦”的图
    if wf < wide:
        poster = img.crop((0, 0, wf, int(wf * 1.42)))
        poster.save(path_poster, quality=95)  # quality=95 是无损crop，如果不设置，默认75
        print('    >poster.jpg裁剪成功')
    else:
        x_left = wf - wide
        poster = img.crop((x_left, 0, wf, hf))    # poster在fanart的 左上角(x_left, 0)，右下角(x_left + wide, hf)
        poster.save(path_poster, quality=95)                 # 坐标轴的Y轴是反的
        print('    >poster.jpg裁剪成功')


# 功能: 不使用人体分析，裁剪fanart封面作为poster，裁剪中间，或者裁剪右边
# 参数: 已下载的fanart路径，目标poster路径， 选择模式int_pattern（无码是裁剪fanart右边，FC2和素人是裁剪fanart中间）
# 返回: 无
# 辅助: Image.open
def crop_poster_default(path_fanart, path_poster, int_pattern):
    img = Image.open(path_fanart)
    wf, hf = img.size  # fanart的宽 高
    wide = int(hf * 2 / 3)  # 理想中海报的宽，应该是fanart的高的三分之二
    # 如果fanart特别“瘦”（宽不到高的三分之二），则以fanart现在的宽作为poster的宽，未来的高为宽的二分之三。
    if wf < wide:
        poster = img.crop((0, 0, wf, wf * 1.5))
        poster.save(path_poster, quality=95)  # quality=95 是无损crop，如果不设置，默认75
        print('    >poster.jpg裁剪成功')
    else:
        x_left = (wf - wide) / int_pattern  # / 2，poster裁剪fanart中间；/ 1，poster裁剪fanart右边。
        # crop
        try:
            poster = img.crop((x_left, 0, x_left + wide, hf))    # poster在fanart的 左上角(x_left, 0)，右下角(x_left + wide, hf)
        except:
            raise
        poster.save(path_poster, quality=95)
        print('    >poster.jpg裁剪成功')


# 功能: 使用人体分析，裁剪fanart封面作为poster，围绕鼻子坐标进行裁剪
# 参数: 已下载的fanart路径，目标poster路径， 百度人体分析client
# 返回: 无
# 辅助: Image.open, image_cut()
def crop_poster_baidu(path_fanart, path_poster, client):
    img = Image.open(path_fanart)
    wf, hf = img.size  # fanart的宽 高
    wide = int(hf * 2 / 3)  # 理想中海报的宽，应该是fanart的高的三分之二
    # 如果fanart特别“瘦”，宽不到高的三分之二。以fanart的宽作为poster的宽。
    if wf < wide:
        poster = img.crop((0, 0, wf, wf * 1.5))
        poster.save(path_poster, quality=95)  # quality=95 是无损crop，如果不设置，默认75
        print('    >poster.jpg裁剪成功')
    else:
        wide_half = wide / 2
        # 使用人体分析，得到鼻子x坐标
        x_nose = image_cut(path_fanart, client)  # 鼻子的x坐标
        # 围绕鼻子进行裁剪，先来判断一下鼻子是不是太靠左或者太靠右
        if x_nose + wide_half > wf:  # 鼻子 + 一半poster宽超出fanart右边
            x_left = wf - wide  # 以右边为poster
        elif x_nose - wide_half < 0:  # 鼻子 - 一半poster宽超出fanart左边
            x_left = 0  # 以左边为poster
        else:  # 不会超出poster
            x_left = x_nose - wide_half  # 以鼻子为中心向两边扩展
        # crop
        poster = img.crop((x_left, 0, x_left + wide, hf))    # poster在fanart的 左上角(x_left, 0)，右下角(x_left + wide, hf)，
        poster.save(path_poster, quality=95)                 # 坐标轴的Y轴是反的
        print('    >poster.jpg裁剪成功')


# 功能: 给poster的左上方加上“中文字幕”的红色条幅
# 参数: poster路径
# 返回: 无
# 辅助: Image.open
def add_watermark_subtitle(path_poster):
    # 打开poster，“中文字幕”条幅的宽高是poster的宽的四分之一
    img_poster = Image.open(path_poster)
    scroll_wide = int(img_poster.height/4)
    # 打开“中文字幕”条幅，缩小到合适poster的尺寸
    watermark_subtitle = Image.open('StaticFiles/subtitle.png')
    watermark_subtitle = watermark_subtitle.resize((scroll_wide, scroll_wide), Image.ANTIALIAS)
    r, g, b, a = watermark_subtitle.split()    # 获取颜色通道，保持png的透明性
    # 条幅在poster上摆放的位置。左上角（0，0）
    img_poster.paste(watermark_subtitle, (0, 0), mask=a)
    img_poster.save(path_poster, quality=95)
    print('    >poster加上中文字幕条幅')


# 功能: 给poster的右上方加上“无码流出”的红色条幅
# 参数: poster路径
# 返回: 无
# 辅助: Image.open
def add_watermark_divulge(path_poster):
    # 打开poster，条幅的宽高是poster的宽的四分之一
    img_poster = Image.open(path_poster)
    w, h = img_poster.size
    scroll_wide = int(h/4)
    # 打开条幅，缩小到合适poster的尺寸
    watermark_divulge = Image.open('StaticFiles/divulge.png')
    watermark_divulge = watermark_divulge.resize((scroll_wide, scroll_wide), Image.ANTIALIAS)
    r, g, b, a = watermark_divulge.split()    # 获取颜色通道，保持png的透明性
    # 条幅在poster上摆放的位置。左上角（x_left，0）
    x_left = w - scroll_wide
    img_poster.paste(watermark_divulge, (x_left, 0), mask=a)
    img_poster.save(path_poster, quality=95)
    print('    >poster加上无码流出红幅')
