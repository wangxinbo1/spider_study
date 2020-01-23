# -*- coding: UTF-8 -*-
'''=================================================
@Project -> File   ：study_start -> tiezi_title
@IDE    ：PyCharm
@Author ：Mr. wang
@Date   ：2020/1/3 0003 19:38
@Desc   ：
=================================================='''
from lxml import etree
import requests
import re
import time
from spider import set_up_pre
from spider.mysql_spider import MysqlManage

mysql_mgr = MysqlManage()

# 1.分析url中的规则

class  GetTieZiTitle():

    def get_certain_page_html(self, page_index):
        url = 'http://www.newsmth.net/nForum/board/AutoWorld?ajax&p={}'.format(page_index)
        res = requests.get(url, headers=set_up_pre.headers)
        return res.text
        time.sleep(set_up_pre.speed_rate)
        print(res.text)

# 2.分析元素,获取内容
    def get_max_page(self, content_html):
        pass
        tree = etree.HTML(content_html)
        lis = tree.xpath('//div[@class="t-pre"]//ol/li')
        if len(lis) == 1:
            return 1
        if lis[-1].xpath('a')[0].text == ">>":
            return lis[-2].xpath('a')[0].text
        return lis[-1].xpath('a')[0].text

    def extract_text(self,columns,index):
        tt = columns[index].text
        return tt if tt is not None else 0

    def get_content(self, content_html):
        tree = etree.HTML(content_html)
        trs = tree.xpath('//table[@class="board-list tiz"]/tbody/tr')
        result_list = []

        for tr in trs:
            result_dict = {}
            td = tr.xpath('td')
            result_dict["title"]=td[1].xpath('a')[0].text
            result_dict["url"]=td[1].xpath('a')[0].attrib["href"]
            result_dict["publish_time"]=td[2].text
            result_dict["author_url"] = td[3].xpath('a')[0].attrib["href"]
            result_dict["author_id"]=td[3].xpath('a')[0].text
            result_dict["rating"]=self.extract_text(td,4)
            result_dict["like_cnt"]=self.extract_text(td,5)
            result_dict["reply_cnt"]=self.extract_text(td,6)
            result_dict["queue_time"]=td[7].xpath('a')[0].text
            result_list.append(result_dict)
            mysql_mgr.insert_topic(result_dict)
        return result_list


if __name__== "__main__":
    get_title = GetTieZiTitle()
    content = get_title.get_certain_page_html(1)
    page_size = get_title.get_max_page(content)
    # print(get_title.get_content(content))
    for i in range(1,3):
        content = get_title.get_certain_page_html(i)
        result = get_title.get_content(content)
        print(result)
        if i==5:
            break

