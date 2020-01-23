# -*- coding: UTF-8 -*-
'''=================================================
@Project -> File   ：study_start -> spider_weiji
@IDE    ：PyCharm
@Author ：Mr. wang
@Date   ：2019/12/29 0029 12:02
@Desc   ：
=================================================='''
import requests
from lxml import etree
import re

with open("aobama.html", encoding="utf-8") as fs:
    contents = fs.read()

# contents = re.sub("\\n",'',contents)
# print(contents)
tree = etree.HTML(contents)
a = tree.xpath('//*[@id="mw-content-text"]/div/table[1]/tbody/tr')
# print(len(a),a)
for i in a:
    try:
        th = i.xpath("th")
        th = etree.tostring(th[0], encoding="utf-8").decode("utf-8")
        th  = re.sub("<.*?>","",th)
        # print(th)

        td = i.xpath("td")
        td = etree.tostring(td[0], encoding="utf-8").decode("utf-8")
        td = re.sub("<.*?>", "", td)
        td = re.sub("\W*", "", td)
        print(th+":",td)
        print()

    except Exception as err:
        # print("err为", err)
        pass

