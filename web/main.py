# -*- coding: utf-8 -*-
'''
Created on Thursday 21st, December, 2017
@auther: REBOOT
'''

from flask import Flask, render_template, request, jsonify

from search_engine import SearchEngine
from parse_query import myquery
from engine import Engine
from datetime import *

from aip import AipNlp
import xml.etree.ElementTree as ET
import sqlite3
import configparser
import time
import json
import operator
import marshal

import jieba

app = Flask(__name__)

doc_dir_path = ''
db_path = ''
wordbank_path = ''
global page
global keys

def init():
	config = configparser.ConfigParser()
	config.read('../config.ini', 'utf-8')
	global dir_path, db_path
	dir_path = config['DEFAULT']['doc_dir_path']
	db_path = config['DEFAULT']['db_path']
	wordbank_path = config['DEFAULT']['wordbank_path']

@app.route('/')
@app.route('/search.html')
def main():
	docs = []
	init()
	docs = suggest_hot()
	return render_template('search.html', docs = docs, error = True)


# 读取表单数据，获得doc_ID
@app.route('/search/', methods = ['POST'])
def search():
	query = {}
	sug_docs = []
	print("enter search: ")
	try:
		global keys
		global checked
		checked = ['checked="true"', '', '']
		keys = request.form['key_word']
		print(keys)

		mq = myquery()
		query = mq.parse_query(keys)
		print("get original query: "+"\n")
		print(query)

		myeng = Engine()
		result = myeng.search(query)
		print("已经获取结果：")
		print(result)
		bool_term, k_term = result[0], result[1]
		print("结果划分：")
		print(bool_term)
		print(k_term)
		k_word = []

		sug_docs = suggest_hot()
		print(len(sug_docs))
		sug_docs = sug_docs[0:10]
		print(len(sug_docs))

		f = open("../data/kindex1.dat", "rb")
		f = marshal.load(f)
		for term in k_term:
			for word in f.keys():
				if term == word:
					for i in f[word]:
						k_word.append(i)
		print("获取通配符检索词项：")
		print(k_word)
		print(bool_term)
		merged_keys = list(set(bool_term + k_word))
		print("合并布尔检索和通配符检索词项：")
		print(merged_keys)



		if keys not in ['']:
			print("aaaaaa")
			print(time.clock())
			print("bbbbbbb")
			flag, page = searchidlist(merged_keys)
			print("ccccccc")
			if flag == 0:
				docs = []
				docs = suggest_hot()
				return render_template('search.html', docs=docs, error=True)
			print("dddddd")
			docs = cut_page(page, 0)
			print(len(docs))
			print(time.clock())
			print("ffffff")

			return render_template('high_search.html', checked = checked, key = keys, sug_docs = sug_docs, docs = docs, page_no=1, page = page, error = True)
		else:
			docs = []
			docs = suggest_hot()
			return render_template('search.html', docs=docs, error = True)

	except:
		print('main search error')

# 评论情感分析
def feel_analyse(sentence):
	APP_ID = '10637556'
	API_KEY = 'rm0HA7EqfQ16HdOZMqwHkho5'
	SECRET_KEY = '3rM91Nj9Z3aLarTgMqvbexdwl0fN3vNd'
	client = AipNlp(APP_ID, API_KEY, SECRET_KEY)
	# text="这个东西很赞"
	print("开始处理情感：")
	sentence = ''.join(e for e in sentence if e.isalnum())
	if len(sentence) < 1:
		return 1
	resp = client.sentimentClassify(sentence)
	print(resp)
	sentiment = resp['items'][0]['sentiment']

	return sentiment

# 搜索主页热点新闻推荐
def suggest_hot():
	docs = []
	news_data = []
	try:
		with open("../data/wangyilogs.json", encoding = 'utf-8') as f:
			for line in f:
				news_data.append(json.loads(line))
		news_data = sorted(news_data, key=lambda k: k['comment_num'], reverse=True)
	# news_data.reverse()
	# print(news_data[0]['comment_num'])
	# print(news_data[50]['comment_num'])
	except:
		print("suggest top hot failed!")
	print("检查 news_data 的大小："+str(len(news_data)))

	comment_con = ""

	for i in range(0, 100):
		com_con = []
		url = news_data[i]['url']
		title = news_data[i]['title']
		keyword = ' '.join(news_data[i]['keyword'])
		category = news_data[i]['category']
		time = news_data[i]['pub_time']
		source = news_data[i]['source']
		comment_url = news_data[i]['comment_url']
		comment_num = news_data[i]['comment_num']
		comment_joinnum = news_data[i]['comment_joinnum']

		if 'comment_con' in news_data[i]:
			comment_con = news_data[i]['comment_con'].split(',')
			print("处理评论：")
			print(len(comment_con))
			for com in comment_con:
				if com != '':
					one = com.split(':')
					print(one)

					print("情感分析之后：")
					print(one)
					# one[0] = one[0].split("'")[1]
					# one[1] = one[1].split("'")[1]
					# print(one)
					com_con.append(one)
				else:
					continue
		print("处理之后：")
		print(com_con)

		print("退出处理：")
		body = news_data[i]['content']
		snippet = news_data[i]['content'][0:120] + '......'

		doc = {'url': url, 'title': title, 'snippet': snippet, 'datetime': str(datetime.now()), 'time': time, 'body': body,
               'id': i, 'extra': [], 'keyword': keyword, 'category': category, 'source': source, 
               'comment_url': comment_url, 'comment_con': com_con, 'comment_num': comment_num, 'comment_joinnum': comment_joinnum}
		docs.append(doc)
	print("输出评论：")
	# print(docs[50]['comment_con'])
	print("检查 docs 的大小：")
	print(len(docs))
	mydoc = []
	for i in range(0,8):
		mydoc.append(docs[i])

	# return render_template('search.html', docs = mydoc, error = True)
	return docs


def searchidlist(key, selected = 0):
	global page
	global doc_id
	se = SearchEngine('../config.ini', 'utf-8')
	flag, id_scores = se.search(key, selected)
	# 返回docid列表
	doc_id = [i for i, s in id_scores]
	print(doc_id)
	page = []
	for i in range(1, (len(doc_id) // 10 + 2)):
		page.append(i)
	print(page)
	return flag,page

def cut_page(page, no):
	print("enter cut_page: ")
	docs = find(doc_id[no*10:page[no]*10])
	print("quit cut_page: ")
	return docs

# 将需要的数据以字典的形式打包传递给search函数
def find(docid, extra=False):
	global dir_path, db_path
	docs = []
	news_data = []
	print("enter find: ")
	print("doc_dir_path: " + dir_path)
	with open(dir_path, encoding = 'utf-8') as f:
			for line in f:
				news_data.append(json.loads(line))
	
	print("enter find_for: ")
	for id in docid:
		com_con = []
		print(id)
		id = int(id)
		print(id)
		comment_con = ""
		print("get url: " + news_data[id]['url'])
		url = news_data[id]['url']
		print("url: "+url)
		title = news_data[id]['title']
		print("title: "+ title)
		keyword = ' '.join(news_data[id]['keyword'])
		print("keyword: "+ keyword)
		category = news_data[id]['category']
		time = news_data[id]['pub_time']
		source = news_data[id]['source']
		comment_url = news_data[id]['comment_url']
		comment_num = news_data[id]['comment_num']
		comment_joinnum = news_data[id]['comment_joinnum']
		print("check comment_con exist: ")
		if 'comment_con' in news_data[id]:
			comment_con = news_data[id]['comment_con'].split(',')
			print("处理评论：")
			print(len(comment_con))
			for com in comment_con:
				if com != '':
					one = com.split(':')
					print(one)
					# one[0] = one[0].split("'")[1]
					# one[1] = one[1].split("'")[1]
					# print(one)
					com_con.append(one)
				else:
					continue
		print("处理之后：")
		print(com_con)
		print("get body: ")
		body = news_data[id]['content']
		snippet = news_data[id]['content'][0:120] + '......'

		doc = {'url': url, 'title': title, 'snippet': snippet, 'datetime': str(datetime.now()), 'time': time, 'body': body,
               'id': id, 'extra': [], 'keyword': keyword, 'category': category, 'source': source, 
               'comment_url': comment_url, 'comment_con': com_con, 'comment_num': comment_num, 'comment_joinnum': comment_joinnum}
		print("hhhhhhhhhhh")

		if extra:
			print("start get k nearest page: ")
			temp_doc = get_k_nearest(db_path, id)
			print(" quit get k nearest page: ")
			for i in temp_doc:
				i = int(i)
				title = news_data[i]['title']
				url = news_data[i]['url']
				time = news_data[i]['pub_time']
				source = news_data[i]['source']
				category = news_data[i]['category']
				doc['extra'].append({'time':time,'id': i, 'title': title, 'url':url, 'source':source, 'category':category})
		docs.append(doc)
	print("输出评论：")
	print(len(docs))
	# print(docs[2]['comment_con'])
	return docs

# 首页推荐最热的社会新闻
@app.route('/search/top_suggest/', methods = ['GET', 'POST'])
def top_hot():
	docs = []
	news_data = []
	try:
		with open("../data/wangyilogs.json", encoding = 'utf-8') as f:
			for line in f:
				news_data.append(json.loads(line))
		news_data = sorted(news_data, key=lambda k: k['comment_num'], reverse=True)
	# news_data.reverse()
	# print(news_data[0]['comment_num'])
	# print(news_data[50]['comment_num'])
	except:
		print("suggest top hot failed!")
	print("检查 news_data 的大小："+str(len(news_data)))

	comment_con = ""

	for i in range(0, 100):
		com_con = []
		url = news_data[i]['url']
		title = news_data[i]['title']
		keyword = ' '.join(news_data[i]['keyword'])
		category = news_data[i]['category']
		time = news_data[i]['pub_time']
		source = news_data[i]['source']
		comment_url = news_data[i]['comment_url']
		comment_num = news_data[i]['comment_num']
		comment_joinnum = news_data[i]['comment_joinnum']
		if 'comment_con' in news_data[i]:
			comment_con = news_data[i]['comment_con'].split(',')
			print("处理评论：")
			print(len(comment_con))
			for com in comment_con:
				if com != '':
					one = com.split(':')
					print(one)
					# one[0] = one[0].split("'")[1]
					# one[1] = one[1].split("'")[1]
					# print(one)
					com_con.append(one)
				else:
					continue
		print("处理之后：")
		print(com_con)
		body = news_data[i]['content']
		snippet = news_data[i]['content'][0:120] + '......'

		doc = {'url': url, 'title': title, 'snippet': snippet, 'datetime': str(datetime.now()), 'time': time, 'body': body,
               'id': i, 'extra': [], 'keyword': keyword, 'category': category, 'source': source, 
               'comment_url': comment_url, 'comment_con': com_con, 'comment_num': comment_num, 'comment_joinnum': comment_joinnum}
		docs.append(doc)
	print("输出评论：")
	# print(docs[50]['comment_con'])
	print("检查 docs 的大小：")
	print(len(docs))
	mydoc = []
	for i in range(0,8):
		mydoc.append(docs[i])

	return render_template('search.html', docs = mydoc, error = True)
	# return jsonify(docs)

@app.route('/search/page/<page_no>/', methods = ['GET'])
def next_page(page_no):
	sug_docs = []
	try:
		page_no = int(page_no)
		docs = cut_page(page, (page_no-1))

		# 搜索结果页热点新闻推荐
		sug_docs = suggest_hot()
		# print(len(sug_docs))
		sug_docs = sug_docs[0:10]

		return render_template('high_search.html', checked=checked, key=keys, sug_docs=sug_docs, docs=docs, page_no=page_no, page=page, error=True)
	except:
		print('next error')

@app.route('/search/<key>/', methods=['POST'])
def high_search(key):
	sug_docs = []
	try:
		print("enter high_search: ")
		selected = int(request.form['order'])
		print(selected)
		for i in range(3):
			if i == selected:
				checked[i] = 'checked="true"'
			else:
				checked[i] = ''
		print("mymymymymmymymym")
		print(key)
		flag, page = searchidlist(key, selected)
		print(page)

		# 搜索主页热点新闻推荐
		sug_docs = suggest_hot()
		# print(len(sug_docs))
		sug_docs = sug_docs[0:10]

		if flag==0:
			docs = []
			docs = suggest_hot()
			return render_template('search.html', docs=docs, error = True)
		docs = cut_page(page, 0)
		return render_template('high_search.html', checked=checked, key=keys, sug_docs=sug_docs, docs=docs, page_no=1, page=page, error=True)
	except:
		print('high search error')

@app.route('/search/<id>/', methods=['GET', 'POST'])
def content(id):
	try:
		doc = onefind([id], extra = True)
		return render_template('content.html', doc=doc[0])
	except:
		print('content error')




# 将需要的数据以字典的形式打包传递给search函数
def onefind(docid, extra=False):
	global dir_path, db_path
	docs = []
	news_data = []
	print("enter find: ")
	print("doc_dir_path: " + dir_path)
	with open(dir_path, encoding = 'utf-8') as f:
			for line in f:
				news_data.append(json.loads(line))
	
	print("enter find_for: ")
	for id in docid:
		com_con = []
		print(id)
		id = int(id)
		print(id)
		comment_con = ""
		print("get url: " + news_data[id]['url'])
		url = news_data[id]['url']
		print("url: "+url)
		title = news_data[id]['title']
		print("title: "+ title)
		keyword = ' '.join(news_data[id]['keyword'])
		print("keyword: "+ keyword)
		category = news_data[id]['category']
		time = news_data[id]['pub_time']
		source = news_data[id]['source']
		comment_url = news_data[id]['comment_url']
		comment_num = news_data[id]['comment_num']
		comment_joinnum = news_data[id]['comment_joinnum']
		print("check comment_con exist: ")
		if 'comment_con' in news_data[id]:
			comment_con = news_data[id]['comment_con'].split(',')
			print("处理评论：")
			print(len(comment_con))
			for com in comment_con:
				if com != '' and len(comment_con) <= 20:
					one = com.split(':')
					if len(one) > 1:
						print(one[1])
						fee = feel_analyse(one[1])
						if fee == 0:
							one.append("负向")
						elif fee == 1:
							one.append("中性")
						else:
							one.append("正向")
					else:
						continue
					print(one)
					# one[0] = one[0].split("'")[1]
					# one[1] = one[1].split("'")[1]
					# print(one)
					com_con.append(one)
				else:
					continue
		print("处理之后：")
		print(com_con)
		print("get body: ")
		body = news_data[id]['content']
		snippet = news_data[id]['content'][0:120] + '......'

		doc = {'url': url, 'title': title, 'snippet': snippet, 'datetime': str(datetime.now()), 'time': time, 'body': body,
               'id': id, 'extra': [], 'keyword': keyword, 'category': category, 'source': source, 
               'comment_url': comment_url, 'comment_con': com_con, 'comment_num': comment_num, 'comment_joinnum': comment_joinnum}
		print("hhhhhhhhhhh")

		if extra:
			print("start get k nearest page: ")
			temp_doc = get_k_nearest(db_path, id)
			print(" quit get k nearest page: ")
			for i in temp_doc:
				i = int(i)
				title = news_data[i]['title']
				url = news_data[i]['url']
				time = news_data[i]['pub_time']
				source = news_data[i]['source']
				category = news_data[i]['category']
				doc['extra'].append({'time':time,'id': i, 'title': title, 'url':url, 'source':source, 'category':category})
		docs.append(doc)
	print("输出评论：")
	print(len(docs))
	# print(docs[2]['comment_con'])
	return docs





@app.route('/similar/search/<id>/', methods=['GET', 'POST'])
def simidoc(id):
	print("enter simidoc: ")
	id = int(id)
	docs = []
	simi_doc = []
	sug_docs = []
	try:
		simi_doc = get_k_nearest(db_path, id, 30)
		print(simi_doc)
		page = []
		for i in range(1, (len(simi_doc) // 10 + 2)):
			page.append(i)
		print("展示相似文档")
		docs = find(simi_doc[0*10:(page[0]*10 if page[0]*10 < len(simi_doc) else len(simi_doc))] )
		print("进入高级搜索")

		# 搜索主页热点新闻推荐
		sug_docs = suggest_hot()
		# print(len(sug_docs))
		sug_docs = sug_docs[0:10]

		return render_template('high_search.html', checked = checked, key = keys, sug_docs=sug_docs, docs = docs, page_no=1, page = page, error = True)
	except:
		print('simidoc error')

@app.route('/search/suggest', methods=['POST'])
def get_suggest():
	print("enter get suggest: ")
	try:
		query = request.get_json().get('keyword')
		print(query)
	except:
		print("search suggest error!")
	suggest_word = []
	wordbank = open("../data/wordbank.json", 'r', encoding = 'utf-8')
	wordbank = json.load(wordbank)
	flag = 0
	print("更新前：" + str(len(wordbank)))
	for i in range(0, len(wordbank)):
		if wordbank[i][0].startswith(query):
			suggest_word.append(wordbank[i][0])
			print(wordbank[i][0])
			if wordbank[i][0] == query:
				wordbank[i][1] += 1
				flag = 1
			else:
				continue
		else:
			continue
	if flag == 0:
		wordbank.append([query, 1])

	print("更新后：" + str(len(wordbank)))
	with open("../data/wordbank.json", 'w') as fp:
		json.dump(wordbank, fp)
		fp.close()

	return jsonify(suggest_word)


# get_json surce code.
# def get_json(self, force=False, silent=False, cache=True):
# 	rv = getattr(self, '_cached_json', _missing)
# 	if rv is not _missing:
# 		return rv

# 	if self.mimetype != 'application/json' and not force:
# 		print("not json!")
# 		return None

# 	request_charset = self.mimetype_params.get('charset')
# 	try:
# 		data = _get_data(self, cache)
# 		if request_charset is not None:
# 			rv = json.loads(data, encoding=request_charset)
# 		else:
# 			rv = json.loads(data)
# 	except ValueError as e:
# 		if silent:
# 			print("it is ValueError!")
# 			rv = None
# 		else:
# 			rv = self.on_json_loading_failed(e)
# 	if cache:
# 		self._cached_json = rv
# 	return rv

def get_k_nearest(db_path, docid, k=5):
	print("the K is: " + str(k))
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	c.execute("SELECT * FROM knearest WHERE id=?", (docid,))
	docs = c.fetchone()
	print(len(docs))
	#print(docs)
	return docs[1: 1 + k] # max = 5

if __name__ == '__main__':
	jieba.initialize() # 手动初始化（可选）
	app.run()

