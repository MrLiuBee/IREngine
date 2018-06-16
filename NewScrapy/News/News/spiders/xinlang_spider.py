# -*- coding: utf-8 -*-
import scrapy
import params_xinlang 
from ..items import NewsItem
from ..items import CommentItem
import json
import time
import sys
import datetime 

class XinLangSpider(scrapy.Spider):
    name = 'xinlang'
    reload(sys)
    sys.setdefaultencoding( "utf-8" )
    start_news_category = params_xinlang.start_news_category
    custom_settings = {
     'ITEM_PIPELINES':{'News.pipelines.XinlangPipeline': 600},
    }
    def start_requests(self):   
        
        for category_item in self.start_news_category :
            for i in range(1,1000):
            #for i in range(1,1500):
                category_item_url = category_item + "_"+str(i) + params_xinlang.url_tail 
                if "tech" in category_item:
                    category = "tech"
                    yield scrapy.Request(category_item_url, meta={"category": category},callback=self.parse_tech) 
                elif "mil" in category_item:
                    category = "junshi"
                    yield scrapy.Request(category_item_url,meta={"category": category},callback=self.parse_junshi)    
                else :
                    if "gnxw" in category_item:
                        category = "guonei"
                    elif "gjxw" in category_item:
                        category = "gjxw"
                    elif "shxw" in category_item:
                        category = "shehui"                        
                    yield scrapy.Request(category_item_url, meta={"category": category},callback=self.parse_other) 
    def initNews(self,news_item):
        news_item["url"]=""
        news_item["id"]=""
        news_item["category"]=""
        news_item["title"]=""
        news_item["content"]=""
        news_item["pub_time"]=""
        news_item["keyword"]=""
        news_item["comment_num"]=""
        news_item["comment_joinnum"]=""
        news_item["craw_time"]=""
        news_item["source"]=""
        news_item["comment_url"]=""
        return news_item
    def initComment(self,comment_item):    
        comment_item["id"]=""
        comment_item["comment_con"]=""
        return comment_item
    def parse_junshi(self,response): 
        category = response.meta['category']
        source = "//div[@class='fixList']"
        for i in range(1,9):
            source_1 = source + "/ul[" + str(i) + "]"
            for j in range(1,6):
                news_item = NewsItem()
                news_item = self.initNews(news_item)
                source_2 = source_1 + "/li[" + str(j) + "]/a"
                news_item["url"] = str(response.xpath(source_2+"/@href").extract_first())
                news_item["title"] = response.xpath(source_2 +"/text()").extract_first()
                news_item["category"] = category
                yield scrapy.Request(news_item["url"], meta={"news_item": news_item},
                                 callback=self.parse_junshiContent)  
    
    def parse_tech(self,response):      
        category = response.meta['category']  
        source = "//div[@class='contList']"   
        for i in range(1,31):
            news_item = NewsItem()
            news_item = self.initNews(news_item)
            source_1 = source + "/ul/li[" + str(i) +"]/"
            news_item["url"] = str(response.xpath(source_1+"a/@href").extract_first())
            news_item["title"] = response.xpath(source_1 +"a/text()").extract_first()
            news_item["category"] = category
            time_source = str(response.xpath(source_1 + "/span/text()").extract_first()).split(" ") 
            news_item["source"] = time_source[1]
            news_item["pub_time"] = str(time_source[2]+" " + time_source[3])
#            news_item["pub_time"] = time.strftime("%Y-%m-%d %H:%M:%S",str(time_source[2]+" " + time_source[3]))          
            if(self.timeOff(news_item["pub_time"])==False):
            return
            yield scrapy.Request(news_item["url"], meta={"news_item": news_item},
                                 callback=self.parse_techContent)  
    
    def parse_other(self, response):
        #爬取每个Url      
        category = response.meta['category']
        for i in range(1,41):
            news_item = NewsItem()
            news_item = self.initNews(news_item)
            source = "//*[@id='Main']/div[3]/ul/li["+str(i)+"]"        
            news_item["url"] = str(response.xpath(source+"/a/@href").extract_first())
            news_item["title"] = response.xpath(source+"/a/text()").extract_first()
            news_item["category"] = category
            #对每个url进行解析
            yield scrapy.Request(news_item["url"], meta={"news_item": news_item},
                                 callback=self.parse_otherContent)
    def parse_junshiContent(self,response):    
        news_item = response.meta['news_item']
        news_item["id"] = news_item["url"].split(".")[-2].split("/")[-1]       
#        news_item["pub_time"] = time.strftime("%Y-%m-%d %H:%M:%S",str(response.xpath("//*[@id='top_bar']/div/div[2]/span/text()").extract_first()))    
        news_item["pub_time"] = str(response.xpath("//*[@id='top_bar']/div/div[2]/span/text()").extract_first())              
        if(self.timeOff(news_item["pub_time"])==False):
            return
        news_item["source"] = response.xpath("//*[@id='top_bar']/div/div[2]/a/text()").extract_first()
        if (response.xpath("//*[@id='article']").xpath('string(.)').extract()!=[]):  
            news_item["content"] = response.xpath("//*[@id='article']").xpath('string(.)').extract()[0]
        else :
            news_item["content"] = response.xpath("//div[@id='artibody']//p/text()").extract()
        keywords = str(response.xpath("//*[@id='keywords']").extract_first())
        keyword_list = []
        keywords = str(response.xpath("//*[@id='article-bottom']/div[1]").extract_first())
        number = keywords.count("href")   
        for i in range(1,number+1):
            keyword= response.xpath("//*[@id='article-bottom']/div[1]/a["+str(i)+"]/text()").extract_first()
            keyword_list.append(keyword)
        news_item["keyword"] = keyword_list
        if keyword_list == []:
             number = keywords.count("href")
             for i in range(1,number+1):
                keyword= response.xpath("//*[@id='keywords']/a["+str(i)+"]/text()").extract_first()
                keyword_list.append(keyword)
             news_item["keyword"] = keyword_list
        data_news=response.xpath("/html/head").extract()
        data_news = str(data_news).split("name=\"comment\"")[1]
        data_news = str(data_news).split("=")[1].split("\"")[1]
        channel = data_news.split(":")[0]
        id = data_news.split(":")[1]
        comment_Url = "http://comment5.news.sina.com.cn/comment/skin/default.html?channel="\
                    + channel + "&newsid=" + id + "&style=0"
        news_item["comment_url"] = comment_Url
        comment_url= params_xinlang.commentUrl_head + channel + "&newsid=" + id + \
            "&group=&compress=0&ie=gbk&oe=gbk&page=1&page_size=20"
        
        yield scrapy.Request(comment_url, meta={"news_item": news_item,"channel":channel,"id":id},
                                 callback=self.parse_news_comment)
    def parse_otherContent(self,response):       
        news_item = response.meta['news_item']
        news_item["id"] = news_item["url"].split(".")[-2].split("/")[-1]
        news_item["pub_time"] = str(response.xpath("//*[@id='top_bar']/div/div[2]/span/text()").extract_first())
#        news_item["pub_time"] =time.strftime("%Y-%m-%d %H:%M:%S", str(response.xpath("//*[@id='top_bar']/div/div[2]/span/text()").extract_first()))            
        if(self.timeOff(news_item["pub_time"])==False):
            return
        news_item["source"] = response.xpath("//*[@id='top_bar']/div/div[2]/a/text()").extract_first()
        if (response.xpath("//*[@id='article']").xpath('string(.)').extract()!=[]):  
            news_item["content"] = response.xpath("//*[@id='article']").xpath('string(.)').extract()[0]
        else :
            news_item["content"] = response.xpath("//div[@id='artibody']//p/text()").extract()
        
        keywords = str(response.xpath("//*[@id='keywords']").extract_first())
        keyword_list = []
        number = keywords.count("href")
        for i in range(1,number+1):
            keyword= response.xpath("//*[@id='keywords']/a["+str(i)+"]/text()").extract_first()
            keyword_list.append(keyword)
        news_item["keyword"] = keyword_list
        data_news=response.xpath("/html/head").extract()
        data_news = str(data_news).split("name=\"comment\"")[1]
        data_news = str(data_news).split("=")[1].split("\"")[1]
        channel = data_news.split(":")[0]
        id = data_news.split(":")[1]
        comment_Url = "http://comment5.news.sina.com.cn/comment/skin/default.html?channel="\
                    + channel + "&newsid=" + id + "&style=0"
        news_item["comment_url"] = comment_Url
        comment_url= params_xinlang.commentUrl_head + channel + "&newsid=" + id + \
            "&group=&compress=0&ie=gbk&oe=gbk&page=1&page_size=20"
        
        yield scrapy.Request(comment_url, meta={"news_item": news_item,"channel":channel,"id":id},
                                 callback=self.parse_news_comment)
    
    def parse_techContent(self,response):
        news_item = response.meta['news_item']
        news_item["id"] = news_item["url"].split(".")[-2].split("/")[-1]
        if (response.xpath("//*[@id='article']").xpath('string(.)').extract()!=[]):  
            news_item["content"] = response.xpath("//*[@id='article']").xpath('string(.)').extract()[0]
        else :
            news_item["content"] = response.xpath("//div[@id='artibody']//p/text()").extract()
        
        keywords = str(response.xpath("//*[@id='keywords']").extract_first())
        keyword_list = []
        number = keywords.count("href")
        for i in range(1,number+1):
            keyword= response.xpath("//*[@id='keywords']/a["+str(i)+"]/text()").extract_first()
            keyword_list.append(keyword)
        news_item["keyword"] = keyword_list
        data_news=response.xpath("/html/head").extract()
        data_news = str(data_news).split("name=\"comment\"")[1]
        data_news = str(data_news).split("=")[1].split("\"")[1]
        channel = data_news.split(":")[0]
        id = data_news.split(":")[1]
        comment_Url = "http://comment5.news.sina.com.cn/comment/skin/default.html?channel="\
                    + channel + "&newsid=" + id + "&style=0"
        news_item["comment_url"] = comment_Url
        comment_url= params_xinlang.commentUrl_head + channel + "&newsid=" + id + \
            "&group=&compress=0&ie=gbk&oe=gbk&page=1&page_size=20"
        
        yield scrapy.Request(comment_url, meta={"news_item": news_item,"channel":channel,"id":id},
                                 callback=self.parse_news_comment)    
    def parse_news_comment(self,response):  
        news_item = response.meta['news_item']
        channel = response.meta['channel']
        id = response.meta['id']
        json_array = "".join(response.body)
        comment_con=""
        tep="={"
        json_array = json_array[json_array.index(tep)+len(tep)-1:]
        json_array=json_array.replace('null','None')
        data=eval(json_array)  
        news_item["comment_num"] = data["result"]["count"]["show"]
        news_item["comment_joinnum"] = data["result"]["count"]["total"]
        news_item["craw_time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        yield news_item
        if(news_item["comment_num"] == 0):
            return
        for i in range(1,news_item["comment_num"]//20+1):
            comment_url= params_xinlang.commentUrl_head + channel + "&newsid=" + id + "&group=&compress=0&ie=gbk&oe=gbk&page="+str(i)+"&page_size=20"
            yield scrapy.Request(comment_url, meta={"news_item": news_item},
                                 callback=self.parse_comment)
        
    def parse_comment(self,response):  
        json_array = "".join(response.body)
        tep="={"
        comment_item = CommentItem()
        comment_item=self.initComment(comment_item)
        json_array = json_array[json_array.index(tep)+len(tep)-1:]
        json_array=json_array.replace('null','None')
        data=eval(json_array)  
        news_item = response.meta['news_item']  
        comment_item["id"] = news_item["id"]
        comment_list=[]
        cmntlist = ""
        if 'cmntlist' in data['result']:  
            cmntlist = data['result']['cmntlist']  
        comment_items=''        
        for status_dic in cmntlist:  
            if status_dic['uid']!='0':  
                s=status_dic['content'].decode('UTF-8').encode('GBK')  
                s=s.replace("'""'",'"') 
                s=s.replace("\n",'') 
                s1="u'"+s+"'"  
                try:                          
                    ss=eval(s1)                   
                except:
                    try:  
                        s1='u"'+s+'"'  
                        ss=eval(s1)  
                    except:                            
                        return                     
                comment_items = comment_items + "'"+status_dic['uid']+ "':" + "'"+ss + "'"+","
                comment_item["comment_con"] = comment_items    
        yield comment_item
    def timeOff(self,pub_time):
        today = datetime.date.today() 
        year = pub_time[0:4]
        month = pub_time[7:9]
        day = pub_time[12:14]
        
        strTime = year +"-"+month+"-"+day
        pub = datetime.datetime.strptime(strTime,'%Y-%m-%d')
        
        time_today = time.mktime(today.timetuple())
        time_pub = time.mktime(pub.timetuple())
        
        if(0<time_today-time_pub<86400):
            return True
        else:
            return False