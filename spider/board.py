# -*- coding: UTF-8 -*-
'''=================================================
@Project -> File   ：study_start -> shuimushequ
@IDE    ：PyCharm
@Author ：Mr. wang
@Date   ：2020/1/1 0001 22:39
@Desc   ：
=================================================='''
from lxml import etree
import re
import requests
from spider.mysql_spider import MysqlManage


"""
爬虫三步走：
1. 分析url，将url中的变值设置为变量
2. 定义发送的请求,然后拿到响应文本，也就是html文件
3. 然后根据内容定位相应的元素,拿到文本或者相应的链接内容
http://www.newsmth.net/nForum/section/6?ajax
"""
mysql_mgr = MysqlManage()

class  ShuiMu():
    """
    爬取水木社区
    """
    base_url = "http://www.newsmth.net"

    def post_request(self, board, index=None):
        url = self.base_url + board + str(index) +"?ajax"
        res = requests.get(url)
        # res.encoding = "utf-8"
        return res.text

    def get_board(self, content):

        tree = etree.HTML(content)
        # tree = etree.tostring(tree, encoding="utf-8").decode("utf-8")
        tr_list = tree.xpath('//table[@class="board-list corner"]/tbody/tr')
        results_list = []
        for i in tr_list:
            result_dict={}
            td = i.xpath("td")
            if len(td) == 1:
                break
            result_dict["name"] = td[0].xpath("a")[0].text
            result_dict["url"] = td[0].xpath("a")[0].attrib["href"]
            # print(td[2].xpath('a'))

            if len(td[1].xpath('a')) == 0 and len(td[2].xpath('a')) == 0:
                # print(td[2].xpath('a'))
                # result_dict["mgr_id"] = "此处为二级目录"
                url_xin = self.base_url + result_dict["url"] + "?ajax"
                res_xin = requests.get(url_xin)
                results_list.append(self.get_board(res_xin.text))
                continue
            if len(td[1].xpath('a')) == 0 and len(td[2].xpath('a')) != 0:
                result_dict["mgr_id"] = td[1].text
                result_dict["mgr_url"] = ""
            else:
                result_dict["mgr_id"] = td[1].xpath("a")[0].text
                result_dict["mgr_url"] = td[1].xpath("a")[0].attrib["href"]
            # result_dict["最新主题"] = td[2].xpath("a")[0].text
            # result_dict["在线"] = td[3].text
            # result_dict["今日"] = td[4].text
            result_dict["topics_cnt"] = int(td[5].text)
            result_dict["posts_cnt"] = int(td[6].text)
            mysql_mgr.insert_board(result_dict)
            results_list.append(result_dict)
        return results_list

if __name__=="__main__":
    import time
    sm = ShuiMu()
    content = sm.post_request("/nForum/section/",6)
    time.sleep(3)
    # print(content)
    result = sm.get_board(content)
    print(result)