# -*- coding: utf-8 -*-
'''
Created on Thursday 21st, December, 2017
@auther: REBOOT
'''

from os import listdir
from lxml import etree
from kindex_gen import Kgen
import xml.etree.ElementTree as ET
import jieba
import sqlite3
import configparser
import json

class Doc:
	docid = 0
	date_time = ''
	comment_num = 0
	comment_joinnum = 0
	tf = 0
	ld = 0
	def __init__(self, docid, date_time, comment_num, comment_joinnum, tf, ld):
		self.docid = docid
		self.date_time = date_time
		self.comment_num = comment_num
		self.comment_joinnum = comment_joinnum
		self.tf = tf
		self.ld = ld
	def __repr__(self):
		return(str(self.docid) + '\t' + self.date_time + '\t'+ str(self.comment_num) + '\t' + str(self.comment_joinnum) + '\t' + str(self.tf) + '\t' + str(self.ld))
	def __str__(self):
		return(str(self.docid) + '\t' + self.date_time + '\t'+ str(self.comment_num) + '\t' + str(self.comment_joinnum) + '\t' + str(self.tf) + '\t' + str(self.ld))

class IndexModule:
	stop_words = set()
	postings_lists = {}
	cleaned_list = []

	config_path = ''
	config_encoding = ''

	def __init__(self, config_path, config_encoding):
		self.config_path = config_path
		self.config_encoding = config_encoding
		config = configparser.ConfigParser()
		config.read(config_path, config_encoding)
		f = open(config['DEFAULT']['stop_words_path'], encoding = config['DEFAULT']['stop_words_encoding'])
		words = f.read()
		self.stop_words = set(words.split('\n'))

	def is_number(self, s):
		try:
			float(s)
			return True
		except ValueError:
			return False

	def clean_list(self, seg_list):
		cleaned_dict = {}
		n = 0
		for i in seg_list:
			i = i.strip().lower()
			if i != '' and not self.is_number(i) and i not in self.stop_words:
				n = n + 1
				if i in cleaned_dict:
					cleaned_dict[i] = cleaned_dict[i] + 1
				else:
					cleaned_dict[i] = 1
		return n, cleaned_dict

	def write_postings_to_db(self, db_path):
		conn = sqlite3.connect(db_path)
		c = conn.cursor()

		c.execute('''DROP TABLE IF EXISTS postings''')
		c.execute('''CREATE TABLE postings
			(term TEXT PRIMARY KEY, df INTEGER, docs TEXT)''')

		for key, value in self.postings_lists.items():
			doc_list = '\n'.join(map(str, value[1]))
			t = (key, value[0], doc_list)
			c.execute("INSERT INTO postings VALUES (?, ?, ?)", t)

		conn.commit()
		conn.close()

	def construct_postings_lists(self):
		news_data = []
		config = configparser.ConfigParser()
		config.read(self.config_path, self.config_encoding)
		with open(config['DEFAULT']['doc_dir_path'], encoding = config['DEFAULT']['doc_encoding']) as f:
			for line in f:
				news_data.append(json.loads(line))
		AVG_L = 0
		
		for i in range(0, len(news_data)):
			keyword = ' '.join(news_data[i]['keyword'])
			comment_num = news_data[i]['comment_num']
			comment_joinnum = news_data[i]['comment_joinnum']
			title = news_data[i]['title']
			body = news_data[i]['content']
			docid = i
			date_time = news_data[i]['pub_time']

			seg_list = jieba.lcut(title + '。' + keyword + body, cut_all = False)

			ld, cleaned_dict = self.clean_list(seg_list)

			# Kgen.execute(cleaned_dict)

			print("进入外层循环：")
			# print(cleaned_dict)

			AVG_L = AVG_L + ld

			for key, value in cleaned_dict.items():
				d = Doc(docid, date_time,comment_num, comment_joinnum, value, ld)
				if key in self.postings_lists:
					self.postings_lists[key][0] = self.postings_lists[key][0] + 1 # df++
					self.postings_lists[key][1].append(d)
				else:
					self.postings_lists[key] = [1, [d]] #[df, [Doc]]

		for item in self.postings_lists.keys():
			self.cleaned_list.append(item)
		print("得到词项列表：")
		print(self.cleaned_list)
		Kgen().execute(self.cleaned_list)

		AVG_L = AVG_L / len(news_data)
		config.set('DEFAULT', 'N', str(len(news_data)))
		config.set('DEFAULT', 'avg_l', str(AVG_L))
		with open(self.config_path, 'w', encoding = self.config_encoding) as configfile:
			config.write(configfile)
		self.write_postings_to_db(config['DEFAULT']['db_path'])

if __name__ == "__main__":
	im = IndexModule('../config.ini', 'utf-8')
	im.construct_postings_lists()


