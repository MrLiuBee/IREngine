# -*- coding: utf-8 -*-
import json
from operator import itemgetter

def top_hot():
	news_data = []
	# try:
	with open("../data/news/wangyilogs.json") as f:
		for line in f:
			news_data.append(json.loads(line))
	# print(news_data[0])
	# sorted(l, key=itemgetter('comment_num'), reverse=True)
	news_data = sorted(news_data, key=lambda k: k['comment_num'], reverse=True)
	# news_data.reverse()
	print(news_data[0]['comment_num'])
	print(news_data[50]['comment_num'])
	# except:
	# 	print("suggest top hot failed!")

top_hot()
