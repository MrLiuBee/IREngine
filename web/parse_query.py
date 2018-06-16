# -*- coding: utf-8 -*-

import re

class myquery:
	line = None
	def parse_query(self, line):
		"""Parse all three kinds of query terms into a dict"""
		print("enter parse query: ")
		query = {'bool': [], 'phrase': [], 'wild': []}
		print("初步处理查询字符串：")
		self.line  = re.sub(r'[_]|[^\w\s"*]', ' ', line.strip().lower())
		print("初步处理之后：")
		# self.line = line
		print(self.line)
		query = self.parse_wildcard(query)
		query = self.parse_phrase(query)
		query = self.parse_boolean(query)
		print("返回处理后的数据")
		return query

	def parse_wildcard(self, query):
		print("enter wildcard parse: ")
		"""Extract wildcard queries into query{}"""
		regex = r"([\w]+)?([\*])([\w]+)?"
		query['wild'] = re.findall(regex, self.line)
		if query['wild']:
		  self.line = re.sub(regex, '', self.line)
		  for i in range(len(query['wild'])):
		    query['wild'][i] = list(filter(len, query['wild'][i]))
		return query

	def parse_phrase(self, query):
		print("enter parse phrase: ")
		"""extract phrase query terms into query{}"""
		regex = r'\w*"([^"]*)"'
		query['phrase'] = re.findall(regex, self.line)
		if query['phrase']:
		  self.line = re.sub(regex, '', self.line)
		return query

	def parse_boolean(self, query):
		print("enter parse boolean: ")
		"""Consider whatever is left as boolean query terms"""
		query['bool'] = self.line.split()
		return query

	def parse_test(self):
		# line = "(walk|walked|walking) (sth|sth.|something) \boff\b"
		line = "\S?+_VV?\w*\saction_N\w+"
		result = self.parse_query(line)
		print(result)
