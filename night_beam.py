import random

import numpy as np
np.set_printoptions(suppress=True)
from tqdm import tqdm
from PIL import Image, ImageDraw, ImageFont

import rimo.cv0 as cv2


def 写字(text, 原图=None):
    if 原图 is None:
        array = np.ones((40, 720), np.uint8) * 255
        image = Image.fromarray(array)
    else:
        image = Image.fromarray(原图)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("consola.ttf", 32, encoding="unic")
    draw.text((0, 0), text, 0, font)
    return np.asarray(image).copy()


def 马赛克(img, d=20):
    r, c = img.shape[:2]
    for x in range(0, r, d):
        for y in range(0, c, d):
            img[x:x + d, y:y + d] = np.mean(img[x:x + d, y:y + d])
    return img


def 收缩(img, d=20):
    r, c = img.shape[:2]
    img小 = img[::d, ::d].copy().astype(np.int32)
    img小[:] = 0
    for x in range(0, r, d):
        for y in range(0, c, d):
            img小[x // d, y // d] = np.mean(img[x:x + d, y:y + d])
    return img小.flatten()


字 = 'alice was beginning to get very tired'

糊图 = 马赛克(写字(字))
目标特征 = 收缩(糊图)


def 心(l, 目标特征, 字符集, 位置特征组):
    s = ''.join([random.choice(字符集) for _ in range(l)])

    while True:
        新特征 = 收缩(写字(s))
        差值 = (新特征 - 目标特征)**2
        差值平均 = 差值.mean()
        if 差值平均 == 0:
            return s, 差值, 变更概率
        变更概率 = np.array([(i * 差值).sum() for i in 位置特征组])
        变更概率 /= 变更概率.max()
        试探次数 = 0
        while True:
            试探次数 += 1
            if 试探次数 > 1000:
                print(f'\n')
                print(f'【得到{s}】')
                试探次数 = 0
                新s = ''
                for i, c in enumerate(s):
                    if 变更概率[i] > 10**-4:
                        新s += random.choice(字符集)
                    else:
                        新s += c
                s = 新s
                break
            else:
                新s = ''
                总变更概率 = 变更概率.sum()
                随机抽取 = random.random() * 总变更概率
                for i, c in enumerate(s):
                    随机抽取 -= 变更概率[i]
                    if 随机抽取 < 0:
                        新s += random.choice(字符集)
                        随机抽取 = 999999
                    else:
                        新s += c

                新特征 = 收缩(写字(新s))
                新差值 = (新特征 - 目标特征)**2
                if 新差值.mean() < 差值.mean():
                    print(f'预测: {s}，差值平均: {差值平均}，试探次数: {试探次数}。', end='\r')
                    s = 新s
                    break


def 夜摄(l, 目标特征):
    字符集 = [' ',
           'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
           'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
           ]

    位置特征组 = []
    for i in tqdm(range(l), ncols=50):
        基 = 写字(' ')
        for j in 字符集:
            基 = 写字(' ' * i + j, 基)
        位置特征 = 1 - 收缩(基) / 255
        位置特征组.append(位置特征)
    位置特征组 = np.array(位置特征组)

    s, 差值, 变更概率 = 心(l, 目标特征, 字符集, 位置特征组)
    print('=============')
    print(f'最终结果: {s}')
    print(f'差值: {差值}')
    

夜摄(37, 目标特征)

