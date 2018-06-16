# -*- coding: utf-8 -*-
import scrapy
import params
from ..items import NewsItem
import json
import time
from collections import OrderedDict


class TengxunSpider(scrapy.Spider):
    name = "tengxun"

    def start_requests(self):
        #'http://news.qq.com/world_index.shtml'
        yield scrapy.Request(url='http://news.qq.com/' + '.html', callback=self.parse_news_list)
        yield scrapy.Request(url='http://society.qq.com/' + '.html', callback=self.parse_news_list)
        yield scrapy.Request(url='http://mil.qq.com/mil_index.htm', callback=self.parse_news_list)
        yield scrapy.Request(url='http://cul.qq.com/' + '.html', callback=self.parse_news_list)
        yield scrapy.Request(url='http://ly.qq.com/' + '.html', callback=self.parse_news_list)

    def parse_news_list(self, response):
        # 解析新闻列表，分割每条新闻
        json_array = "".join(response.body[14:-1].split())
        news_array = json.loads(json_array, "gbk")
        news_item = OrderedDict()
        for row in enumerate(news_array):
            news_item = self.generate_news_item(row)
            # 请求新闻正文，并对正文进行解析
            yield scrapy.Request(news_item["url"], meta={"news_item": news_item},
                                 callback=self.parse_news_content, dont_filter=True)

    def generate_news_item(self, row_data):
        print "generate_news_item"
        news_item = NewsItem()
        # 以news_url的末尾随机数作为news_id
        row_data = row_data[1]
        news_item["id"] = row_data["tlink"].split(".")[-2].split("/")[-1]
        news_item["title"] = row_data["title"]
        news_item["url"] = row_data["tlink"]
        news_item["category"] = row_data["channelname"]

        # 2/20/2017171:30:40
 #       timeArray = time.strptime(row_data["time"], "%m/%d/%Y%H:%M:%S")

 #       news_item["pub_time"] = time.strftime("%Y-%m-%d %H:%M:%S",timeArray)
        news_item["pub_time"] = row_data["time"]
        news_item["comment_url"] = row_data["commenturl"]
        news_item["comment_num"] = 0
        news_item["comment_joinnum"] = 0
        news_item["if_hot"] = -1
        news_item["view_num"] = -1

        # 解析新闻关键词
        keyword_list = []
        for key_item in row_data["keywords"]:
            keyword_list.append(key_item["keyname"])
        news_item["keyword"] = keyword_list

        return news_item

    def parse_news_content(self, response):
        print "parse_news_content"
        # 解析新闻页面
        source = "//a[@id='ne_article_source']/text()"
        content_path = "//div[@id='endText']/p/text()"
        # 只提取新闻<p>标签中的内容
        content_list = []
        json_array = "".join(response.body)
        for data_row in response.xpath(content_path).extract():
            content_list.append("".join(data_row.split()))
        content_list = "\"".join(content_list)
        news_item = response.meta['news_item']
        news_item["content"] = content_list
        news_item["source"] = response.xpath(source).extract_first()

        # 提取新闻评论数目和参与数
        comment_url = params.comment_head_url + news_item["id"]

        yield scrapy.Request(comment_url, meta={"news_item": news_item, "comment_url": comment_url},
                             callback=self.Parse_comment_num, dont_filter=True)
