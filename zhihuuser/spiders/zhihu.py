# -*- coding: utf-8 -*-
import json

from scrapy import Spider,Request

from zhihuuser.items import UserItem

"""
    递归爬取某知乎用户的关注列表用户
"""
class ZhihuSpider(Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    start_user = 'zhang-jia-yi-96-10'

    # 用户详情页url
    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'
    user_query =  'allow_message,is_followed,is_following,is_org,is_blocking,employments,answer_count,follower_count,articles_count,gender,badge[?(type=best_answerer)].topics'

    # 用户关注列表详情页url
    follows_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    follows_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    # 用户粉丝列表详情页url
    fans_url = 'https://www.zhihu.com/api/v4/members/{user}/followers?include={include}&offset={offset}&limit={limit}'


    def start_requests(self):

        # 获取爬取用户的详细页，并进行解析
        yield Request(self.user_url.format(user=self.start_user,include=self.user_query),self.parse_user)

        # 获取爬取用户的关注列表，并进行解析
        yield Request(self.follows_url.format(user=self.start_user,include=self.follows_query,offset=0,limit=20),callback=self.parse_follows)

        # 获取爬取用户的粉丝列表，并进行解析
        yield  Request(self.fans_url.format(user=self.start_user,include=self.follows_query,offset=0,limit=20),callback=self.parse_fans)
    # 解析用户详情页
    def parse_user(self, response):
        result = json.loads(response.text)
        item = UserItem()
        for field in item.fields:
            if field in result.keys():
                item[field] = result.get(field)
        yield item

       # 获取用户关注的用户的关注用户
        yield Request(self.follows_url.format(user=result.get('url_token'),include=self.follows_query,limit=20,offset=0),self.parse_follows)
       # 获取用户每个粉丝的粉丝列表
        yield Request(self.fans_url.format(user=result.get('url_token'), include=self.follows_query, limit=20, offset=0),self.parse_fans)

    # 解析用户关注列表页
    def parse_follows(self, response):
        results = json.loads(response.text)
        # 获取关注列表中的用户ID，并解析关注用户的关注列表
        if 'data' in results.keys():
            for result in results.get('data'):
                yield Request(self.user_url.format(user=result.get('url_token'),include=self.user_query),self.parse_user)
        # 判断是否是最后一页，不是获取下一页的url
        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            next_page = results.get('paging').get('next')
            yield Request(next_page,self.parse_follows)

 # 解析用户粉丝列表页
    def parse_fans(self, response):
        results = json.loads(response.text)
        # 获取粉丝列表中的用户ID，并解析粉丝用户的粉丝列表
        if 'data' in results.keys():
            for result in results.get('data'):
                yield Request(self.user_url.format(user=result.get('url_token'),include=self.user_query),self.parse_user)
        # 判断是否是最后一页，不是获取下一页的url
        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            next_page = results.get('paging').get('next')
            yield Request(next_page,self.parse_fans)