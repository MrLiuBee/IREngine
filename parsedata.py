# -*- coding: utf-8 -*-

import json
from datetime import *


file_path = './data/wangyilogs.json'

news_data = []
news_data1 = []
with open(file_path) as f:
	for line in f:
		news_data.append(json.loads(line))

print(len(news_data))

for i in news_data:
	if i not in news_data1:
		news_data1.append(i)


print(len(news_data1))

newdata = open('newdata.json', 'w')
for item in news_data1:
	newdata.write("%s\n" % item)

if 'comment_con' in news_data[200]:
	print("good: ")
else:
	print("bad: ")


a = news_data[12]['comment_con'].split(',')
print(len(news_data[12]['comment_con']))
print(news_data[12]['comment_con'])
print(a[1])
# for i in range(0, len(news_data)):
# 	print(str(news_data[i]['comment_joinnum']))
print(' '.join(news_data[1000]['keyword']))

print("date of now: " + str(datetime.now()))