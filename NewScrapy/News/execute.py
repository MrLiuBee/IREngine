# -*- coding: utf-8 -*-

from scrapy import cmdline
import scrapy
from scrapy.crawler import CrawlerProcess
from News.spiders.wangyi_spider import WangYiSpider
from News.spiders.xinlang_spider import XinLangSpider

process = CrawlerProcess()
process.crawl(WangYiSpider)
process.crawl(XinLangSpider)
process.start() 


#cmdline.execute("scrapy crawl wangyi".split())
#cmdline.execute("scrapy crawl xinlang".split())
#你就能在任何时候安全地停止爬虫(按Ctrl-C或者发送一个信号)。恢复这个爬虫也是同样的命令:
#scrcapy crawl somespider -s JOBDIR=crawls/somespider-1