# -*- coding: utf-8 -*-
'''
Created on Thursday 21st, December, 2017
@auther: REBOOT
'''

from os import listdir
import xml.etree.ElementTree as ET
import jieba
import jieba.analyse
import sqlite3
import configparser
from datetime import *
import math
import json
import pandas as pd
import numpy as np
import operator

from sklearn.metrics import pairwise_distances

class RecommendationModule:
	stop_words = set()
	k_nearest = []

	config_path = ''
	config_encoding = ''

	doc_dir_path = ''
	doc_encoding = ''
	stop_words_path = ''
	stop_words_encoding = ''
	idf_path = ''
	db_path = ''

	def __init__(self, config_path, config_encoding):
		self.config_path = config_path
		self.config_encoding = config_encoding
		config = configparser.ConfigParser()
		config.read(config_path, config_encoding)

		self.doc_dir_path = config['DEFAULT']['doc_dir_path']
		self.doc_encoding = config['DEFAULT']['doc_encoding']
		self.stop_words_path = config['DEFAULT']['stop_words_path']
		self.stop_words_encoding = config['DEFAULT']['stop_words_encoding']
		self.idf_path = config['DEFAULT']['idf_path']
		self.db_path = config['DEFAULT']['db_path']

		f = open(self.stop_words_path, encoding = self.stop_words_encoding)
		words = f.read()
		self.stop_words = set(words.split('\n'))

	def write_k_nearest_matrix_to_db(self):
		conn = sqlite3.connect(self.db_path)
		c = conn.cursor()

		c.execute('''DROP TABLE IF EXISTS knearest''')
		c.execute('''CREATE TABLE knearest
			(id INTEGER PRIMARY KEY, first INTEGER, second INTEGER, 
			third INTEGER, fourth INTEGER, fifth INTEGER)''')

		for docid, doclist in self.k_nearest:
			c.execute("INSERT INTO knearest VALUES (?, ?, ?, ?, ?, ?)", tuple([docid] + doclist))

		conn.commit()
		conn.close()

	def is_number(self, s):
		try:
			float(s)
			return True
		except ValueError:
			return False

	def construct_dt_matrix(self, news_data, topK = 200):
		jieba.analyse.set_stop_words(self.stop_words_path)
		jieba.analyse.set_idf_path(self.idf_path)
		M = len(news_data)
		N = 1
		terms = {}
		dt = []
		for i in range(0, M):
			title = news_data[i]['title']
			keyword = ' '.join(news_data[i]['keyword'])
			body = news_data[i]['content']
			docid = i

			tags = jieba.analyse.extract_tags(title + '。' + keyword + body, topK = topK, withWeight = True)

			cleaned_dict = {}
			for word, tfidf in tags:
				word = word.strip().lower()
				if word == '' or self.is_number(word):
					continue
				cleaned_dict[word] = tfidf
				if word not in terms:
					terms[word] = N
					N += 1
			dt.append([docid, cleaned_dict])
		dt_matrix = [[0 for i in range(N)] for j in range(M)]
		i = 0
		for docid, t_tfidf in dt:
			dt_matrix[i][0] = docid
			for term, tfidf in t_tfidf.items():
				dt_matrix[i][terms[term]] = tfidf
			i += 1

		dt_matrix = pd.DataFrame(dt_matrix)
		dt_matrix.index = dt_matrix[0]
		print('dt_matrix shape:(%d %d)'%(dt_matrix.shape))
		return dt_matrix

	def construct_k_nearest_matrix(self, dt_matrix, k):
		tmp = np.array(1 - pairwise_distances(dt_matrix[dt_matrix.columns[1:]], metric = "cosine"))
		similarity_matrix = pd.DataFrame(tmp, index = dt_matrix.index.tolist(), columns = dt_matrix.index.tolist())
		for i in similarity_matrix.index:
			tmp = [int(i),[]]
			j = 0
			print("construct k nearest matrix iteration: ")
			while j < k:
				max_col = similarity_matrix.loc[i].idxmax(axis = 1)
				similarity_matrix.loc[i][max_col] = -1
				if max_col != i:
					tmp[1].append(int(max_col)) #max column name
					j += 1
			self.k_nearest.append(tmp)

	def gen_idf_file(self):
		news_data = []
		with open(self.doc_dir_path , encoding = 'utf-8') as f:
			for line in f:
				news_data.append(json.loads(line))

		n = float(len(news_data))
		idf = {}
		for i in range(0, len(news_data)):
			keyword = ' '.join(news_data[i]['keyword'])
			title = news_data[i]['title']
			body = news_data[i]['content']

			seg_list = jieba.lcut(title + '。' + keyword + body, cut_all = False)
			seg_list = set(seg_list) - self.stop_words # 去除停用词
			for word in seg_list:
				word = word.strip().lower()
				if word == '' or self.is_number(word):
					continue
				if word not in idf:
					idf[word] = 1
				else:
					idf[word] = idf[word] + 1
		idf_file = open(self.idf_path, 'w', encoding = 'utf-8')
		for word, df in idf.items():
			idf_file.write('%s %.9f\n'%(word, math.log(n / df)))
		idf_file.close()

	def find_k_nearest(self, k, topK):
		self.gen_idf_file()
		news_data = []
		with open(self.doc_dir_path, encoding = 'utf-8') as f:
			for line in f:
				news_data.append(json.loads(line))

		dt_matrix = self.construct_dt_matrix(news_data, topK)
		self.construct_k_nearest_matrix(dt_matrix, k)
		self.write_k_nearest_matrix_to_db()

def generate_wordbank():
	wordbank = {}
	idf_file = open("../data/idf.txt", 'r', encoding = 'utf-8')
	for line in idf_file:
		line = line.split(" ")
		wordbank[line[0]] = int(100*float(line[1]))
	wordbank = sorted(wordbank.items(), key = operator.itemgetter(1))
	wordbank.reverse()

	with open("../data/wordbank.json", 'w') as fp:
		# for i in wordbank:
		# 	json.dump(i, fp)
		json.dump(wordbank, fp)
		fp.close()

	# print(line[0] + " " + str(wordbank[line[0]]))

	# f = idf_file.readline().split(' ')
	# word, fre = f[0], f[1]
	# print (word + " " + fre)

if __name__ == "__main__":
	print('-----start time: %s-----'%(datetime.today()))
	# 下面注释代码为生成 推荐文档，运行时取消注释
	# rm = RecommendationModule('../config.ini', 'utf-8')
	# rm.find_k_nearest(5, 25)

	# 自动补全构建词库
	generate_wordbank()

	# fp = open("../data/wordbank.json", 'r')
	# fp = json.load(fp)
	# print(fp[len(fp)-1][0] + " " + str(fp[len(fp)-1][1]))
	# for i in fp:
	# 	print(i[0] + " " + str(i[1]))
	print('-----finish time: %s-----'%(datetime.today()))

