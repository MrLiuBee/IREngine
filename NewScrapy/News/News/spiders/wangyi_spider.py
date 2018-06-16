# -*- coding: utf-8 -*-
import scrapy
import params
from ..items import NewsItem
from ..items import CommentItem
import json
import time
import sys
import copy

import datetime 
from dateutil.parser import parse


class WangYiSpider(scrapy.Spider):
    name = 'wangyi'
    reload(sys)
    sys.setdefaultencoding( "utf-8" )
    start_news_category = params.start_news_category
    start_sport_category = params.start_sports_category
    custom_settings = {
     'ITEM_PIPELINES':{'News.pipelines.WangyiPipeline': 600},
    }
    def start_requests(self):
        for category_item in self.start_news_category:
            # 最多爬取每个版块前19页数据
           
            category = category_item.split("_")[1]
            for count in range(1, 20):
                if count == 1:
                    start_url = params.news_url_head + category_item + params.news_url_tail
                else:
                    start_url = params.news_url_head + category_item + "_0" + str(count) + params.news_url_tail
                yield scrapy.Request(start_url,meta={"category":category}, callback=self.parse_news_list)
        
        for sports_iterms in self.start_sport_category:
            if "cba" in category_item:
                category = "cba"
            elif "nba" in category_item:
                category = "nba"
            for count in range(1, 20):
                if count == 1:
                    start_url = params.sport_url_head + sports_iterms + params.news_url_tail
                else:
                    start_url = params.sport_url_head + sports_iterms + "_0" + str(count) + params.news_url_tail
                yield scrapy.Request(start_url, meta={"category":category},callback=self.parse_news_list)
    
                
    def parse_news_list(self, response):
        #爬取每个Url
        json_array = "".join(response.body[14:-1].split())
        news_array = json.loads(json_array, "gbk")
        category = response.meta['category']
        for row in enumerate(news_array):
            news_item = NewsItem()
            
            # 以news_url的末尾随机数作为news_id
            row_data=row[1]
            news_item["id"] = row_data["tlink"].split(".")[-2].split("/")[-1]
            news_item["title"] = row_data["title"]
            news_item["url"] = row_data["tlink"]
            news_item["category"] =category
            time_data = row_data["time"].split(" ")
            news_item["pub_time"] = row_data["time"]
            if(self.timeOff(news_item["pub_time"])==False):
                return
            news_item["comment_url"] = row_data["commenturl"]
#            if len(time_data) == 1:
#                time_data = str(time_data).split("2017")
#                times = time_data[0]+"2017" + " " + time_data[1]
#                times = times[1:-1]
                
#                news_item["pub_time"] = time.strftime("%Y-%m-%d %H:%M:%S",times)
#            else:     
#                news_item["pub_time"] = time.strftime("%Y-%m-%d %H:%M:%S",str(row_data["time"]))

            
#            news_item["comment_con"] = {}
            news_item["comment_num"] = ""
            news_item["comment_joinnum"] = ""
#            news_item["if_hot"] = -1
#            news_item["view_num"] = -1
            # 解析新闻关键词
            keyword_list = []
            for key_item in row_data["keywords"]:
                keyword_list.append(key_item["keyname"])
            news_item["keyword"] = keyword_list
            
            yield scrapy.Request(news_item["url"], meta={"news_item":news_item},
                                 callback=self.parse_news_content)
            
    def parse_news_content(self, response):
        #解析新闻页面 
        source = "//a[@id='ne_article_source']/text()"
        content_path = "//div[@id='endText']/p/text()"
        # 只提取新闻<p>标签中的内容
        content_list = []
        for data_row in response.xpath(content_path).extract():
            content_list.append("".join(data_row.split()))
        content_list = "\"".join(content_list)
        news_item = response.meta['news_item']
        news_item["content"] = content_list
        news_item["source"] = response.xpath(source).extract_first()
        
        #提取新闻评论数目和参与数
        comment_url=params.comment_head_url + news_item["id"]
        yield scrapy.Request(comment_url, meta={"news_item":news_item,"comment_url":comment_url},
                                 callback=self.Parse_comment_num)
    
    def Parse_comment_num(self,response):      
        #解析评论
        comment_array = json.loads(response.body, "utf-8")
        news_item = response.meta['news_item']
        comment_url = response.meta['comment_url']    
        news_item["comment_num"] = int(comment_array["tcount"])       
        news_item["comment_joinnum"] = int(comment_array["cmtAgainst"]) + int(comment_array["cmtVote"]) + int(comment_array["rcount"])
        comment_num = news_item["comment_num"]
        comment_item = CommentItem()
        offset = 0
        limit = 30
        index=0
        news_item["craw_time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        comment_item["comment_con"] = ""
        for index in range((comment_num  // limit) + 1):
            offset += index * limit
            comment_urls =self.creatCommentUrl(comment_url,offset,limit)
            # 请求评论列表，返回为json数据
            yield scrapy.Request(comment_urls, meta={"news_item": news_item,"comment_item":comment_item},
                                 callback=self.Parse_comment)
#            request = scrapy.Request(comment_urls, meta={"news_item": news_item})
#            comment= self.Parse_comment(request) 
#        news_item["comment_con"]=comment
        yield news_item
    def Parse_comment(self,response):  
        
        comment_array = json.loads(response.body, "utf-8")        
        news_item = response.meta['news_item']
        comment_item = response.meta['comment_item']
        comment_item["comment_con"] = ""
        comment_item["id"] = news_item["id"]
        comment_items=""
        for comment_id,comment_value in comment_array["comments"].items():
            comment_value = comment_value["content"]
            
            comment_items = comment_items + "'"+comment_id+ "':" + "'"+comment_value + "'"+","
            
        comment_items = comment_items[:-1]  
#        past_comment = comment_item["comment_con"]
#        comment_item["comment_con"] = past_comment+","+comment_items
        comment_item["comment_con"] = comment_items
        if(comment_item["comment_con"]) == "":
            return 
        yield comment_item    
    def creatCommentUrl(self, commenturl, offset, limit):
        start = commenturl
        middle = "/comments/newList?offset="
        url = start + middle + str(offset) + "&limit=" + str(limit)
        
        return url  
    def timeOff(self,pub_time):
        today = datetime.date.today() 
        month = pub_time[0:2]
        day = pub_time[3:5]
        year = pub_time[6:10]
        
        strTime = year +"-"+month+"-"+day
        pub = datetime.datetime.strptime(strTime,'%Y-%m-%d')
        
        time_today = time.mktime(today.timetuple())
        time_pub = time.mktime(pub.timetuple())
        
        if(0<time_today-time_pub<86400):
            return True
        else:
            return False