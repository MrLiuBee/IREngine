# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy import signals
from spiders import wangyi_spider
import scrapy
import json
import codecs
from items import NewsItem
from items import CommentItem
from scrapy.exceptions import DropItem
class DuplicatesPipeline(object):

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['id'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['id'])
            return item

class WangyiPipeline(object):
    def __init__(self):          
#        self.file1 = open(r'F:\Spider\wangyilogs.json', 'wb+')  
#        self.file2 = open(r'F:\Spider\wangyicomments.json', 'wb+')  
        self.file1 = open(r'F:\Spider\wangyilogs.json', 'wb')  
        self.file2 = open(r'F:\Spider\wangyicomments.json', 'wb')  
        
    def process_item(self, item, spider):    
        if isinstance(item, NewsItem):
            line = json.dumps(dict(item), ensure_ascii=False) + "\n"
            self.file1.write(line)
            return item

        # 评论实例
        elif isinstance(item, CommentItem):
            line = json.dumps(dict(item), ensure_ascii=False) + "\n"
            self.file2.write(line)
            return item       
        
    def spider_closed(self, spider):
        self.file1.close()
        self.file2.close()
        
class XinlangPipeline(object):
    def __init__(self):          
#        self.file1 = open(r'F:\Spider\xinlanglogs.json', 'wb+')  
#        self.file2 = open(r'F:\Spider\xinlangcomments.json', 'wb+') 
        
        self.file1 = open(r'F:\Spider\xinlanglogs.json', 'wb')  
        self.file2 = open(r'F:\Spider\xinlangcomments.json', 'wb')  
        
    def process_item(self, item, spider):    
        if isinstance(item, NewsItem):
            line = json.dumps(dict(item), ensure_ascii=False) + "\n"
            self.file1.write(line)
            return item

        # 评论实例
        elif isinstance(item, CommentItem):
            line = json.dumps(dict(item), ensure_ascii=False) + "\n"
            self.file2.write(line)
            return item       
        
    def spider_closed(self, spider):
        self.file1.close()
        self.file2.close()