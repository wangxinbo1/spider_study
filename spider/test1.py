# -*- coding: UTF-8 -*-
'''=================================================
@Project -> File   ：study_start -> test1
@IDE    ：PyCharm
@Author ：Mr. wang
@Date   ：2020/1/4 0004 13:48
@Desc   ：
=================================================='''
from lxml import etree

tree = etree.parse("test1.html",etree.HTMLParser())
# print(tree)
# tree = etree.tostring(tree,encoding="utf-8").decode("utf-8")
# print(type(tree))
span = tree.xpath("//div[contains(@class, 'operating')]//span")
print(span[0].xpath('a'))
