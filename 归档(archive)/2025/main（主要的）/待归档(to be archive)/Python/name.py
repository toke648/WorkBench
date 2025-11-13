from random import randint, choice

man_first_name = "赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹喻柏水窦章云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳酆鲍史唐费廉岑薛雷贺倪汤滕殷罗毕郝邬安常乐于时傅皮卞齐康伍余元卜顾孟平黄和穆萧尹姚邵湛汪祁毛禹狄米贝明臧计伏成戴谈宋茅庞熊纪舒屈项祝董梁杜阮蓝闵席季麻强贾路娄危江童颜郭梅盛林刁钟徐邱骆高夏蔡田樊胡凌霍虞万支柯昝管卢莫经房裘缪干解应宗丁宣贲邓郁单杭洪包诸左石崔吉钮龚程嵇邢滑裴陆荣翁荀羊於惠甄麴家封芮羿储靳汲邴糜松井段富巫乌焦巴弓牧隗山谷车侯宓蓬全郗班仰秋仲伊宫宁仇栾暴甘钭厉戎祖武符刘景詹束龙叶幸司韶郜黎蓟薄印宿白怀蒲邰从鄂"
woman_first_name = '宛、蓉、朵、绮、婷、琼、滢、童、瑶、桦、涵、向、映、珞、澜、紫、月、诗、婧、咏、伊、菁、影、荣、南、千、语、蓓、采、苏、琬、艺、萌、姝、如、夏、毓、梦、姣、雨、梵、莉、琦、沛、汐、虹、依、爱、慕、若、友、易、文、楚、霄、彦、洋、芙、可、婕、逸、媱、丽、琳、冉、琰、灵、妤、洁、馥、雯、静、含、飘、妍、颖、宜、恬、媛、以、筠、荔、冰、淇、倩、玥、白、舒、睿、菲、妮、苇、枫、韵、茜、飞、苑、碧、华、泉'.split('、')
last_name = "谢邹喻柏水窦倪汤滕殷罗毕黄和穆萧尹姚邵禹狄米贝明臧计伏成戴谈宋茅庞熊纪舒屈项祝董梁杜阮蓝闵席樊胡凌经房裘缪干解应宗丁宣贲邓郁单杭洪包诸左石崔景詹束龙叶幸司鄂"

frequency = 6

names = []

for i in range((int(frequency))):
    if randint(1, 3) != 1:
        names.append(choice(man_first_name) + choice(woman_first_name) + choice(man_first_name))
    else:
        names.append(choice(man_first_name) + choice(woman_first_name))


ticks = [randint(30, 80) for i in range(frequency)]

print(names)
print(ticks)

"""
for 循环实现

迭送器实现
"""
# m = []
# for n, t in zip(names, ticks):
#     m.append({'name':n, 'tick':t})
#
# print(m)
result = [{'name': name, 'tick': tick} for name, tick in zip(names, ticks)]

print('生成列表----------\n', result)


import pandas as pd

# ls = {'施狄巴': 33}, {'沈麴宿': 47}, {'童左元': 54}, {'陆全岑': 40}, {'封钭': 47}, {'鲍梅黎': 48}
#
# dictory = [(index, i) for index, i in enumerate(ls)]
#
#
# # print(dictory)
# print(pd.DataFrame(ls))


# ls = ['a', 'b', 'c']
#
# for i in enumerate(ls):
#     print(i)


ls = result

# for i in range(3):
#     name = input()
#     ticket = int(input())
#
#     ls.append({'n':name, '票数': ticket})
# print(ls)
ls.sort(key=lambda x:x['tick'], reverse=True)
print("排序--------\n",ls)
for index, item in enumerate(ls, start=1):
    print(f'第{index}名 {item['name']} {item['tick']}')
