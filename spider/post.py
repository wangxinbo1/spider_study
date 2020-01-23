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

class  GetTieZiContent():

    base_url = 'http://www.newsmth.net'

    def get_certain_page_html(self,topic_url, page):
        params = {"ajax":"","p":str(page)}
        url = self.base_url + topic_url
        res = requests.get(url, headers=set_up_pre.headers,params=params)
        return res.text
        time.sleep(set_up_pre.speed_rate)
        print(res.text)

# 2.分析元素,获取内容
    def get_max_page(self, content_html):
        tree = etree.HTML(content_html)
        lis = tree.xpath('//div[@class="t-pre"]//ol/li')
        if len(lis) == 1:
            return 1
        if lis[-1].xpath('a')[0].text == ">>":
            return lis[-2].xpath('a')[0].text
        return lis[-1].xpath('a')[0].text

    # def get_content(self, content_html):
    #     tree = etree.HTML(content_html)
    #     trs = tree.xpath('//table[@class="board-list tiz"]/tbody/tr')
    #     result_list = []
    #
    #     for tr in trs:
    #         result_dict = {}
    #         td = tr.xpath('td')
    #         result_dict["主题"]=td[1].xpath('a')[0].text
    #         result_dict["url"]=td[1].xpath('a')[0].attrib["href"]
    #         result_list.append(result_dict)
    #
    #     return result_list

    def get_content_detail(self,content_html):
        # if index <= 0:
        #     print("index 必须大于等于1,且为正整数")
        #     return
        # result_list = self.get_content(content_html)
        # # print(result_list)
        # url = self.base_url + result_list[index-1]["url"] + "?ajax"
        # res = requests.get(url,headers=set_up_pre.headers)
        # print(type(res.text))
        tree = etree.HTML(content_html)
        ps = tree.xpath('//div[contains(@class,"a-wrap")]//td/p[1]')
        content_list = []
        for p in ps:
            p = etree.tostring(p,encoding="utf-8").decode("utf-8")
            p = re.sub('<br/>','\n',p)
            p = re.sub("<.*?>",'',p)
            content_list.append(p)
        return content_list

if __name__== "__main__":
    while True:
        topic = mysql_mgr.dequeue_topic()
        print(topic)
        if topic is None:
            exit(1)
        get_post = GetTieZiContent()
        content_html = get_post.get_certain_page_html(topic["url"],1)
        page_size = get_post.get_max_page(content_html)

        posts = get_post.get_content_detail(content_html)


        if int(page_size) > 1:
            for i in range(2,int(page_size)+1):
                content = get_post.get_certain_page_html(topic["url"],i)
                posts =posts+get_post.get_content_detail(content)
                # print(posts)

        i = 0
        for p in posts:
            # print(p)
            # print("=============================", i, "=============================")
            # print("")

            # Compose the post object
            post = {}
            post['topic_id'] = topic['id']
            post['content'] = p
            post['post_index'] = i
            mysql_mgr.insert_post(post)
            i += 1
        print('Post count:', i)
        # Mark this topic as finished downloading
        mysql_mgr.finish_topic(topic['id'])
        print("=============================", i, "=============================")



