# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # define the fields for your item here like:
    # name = scrapy.Field()
    allowed_domains = []
    # 新闻ID
    id = scrapy.Field()
    # 新闻url
    url = scrapy.Field()
    # 新闻所属类（例：互联网、通信、电子）
    category = scrapy.Field()
    # 标题
    title = scrapy.Field()
    # 正文内容（带html标签，包括相关图片）
    content = scrapy.Field()
    # 发布时间
    pub_time = scrapy.Field()
    # 关键词
    keyword = scrapy.Field()
    # 浏览量（无则标-1）
#    view_num = scrapy.Field()
    # 评论数
    comment_num = scrapy.Field()
    # 评论参与数
    comment_joinnum = scrapy.Field()
    # 评论内容（按换行分隔）
#    comment_con = scrapy.Field()
    # 是否热门（标题是否加粗加红）
#    if_hot = scrapy.Field()
    # 爬取时间
    craw_time = scrapy.Field()
    # 来源
    source = scrapy.Field()
    #评论url
    comment_url = scrapy.Field()

class CommentItem(scrapy.Item):
    # 新闻ID
    id = scrapy.Field()
    # 评论内容（按换行分隔）
    comment_con = scrapy.Field()    
    