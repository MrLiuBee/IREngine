 # -*- coding:utf-8 -*-
import re
class myquery:
	line = None
	def parse_query(self, line):
		"""Parse all three kinds of query terms into a dict"""
		query = {'bool': [], 'phrase': [], 'wild': []}
		self.line  = re.sub(r'[_]|[^\w\s"*]', ' ', line.strip().lower())
		# self.line = line
		print(self.line)
		query = self.parse_wildcard(query)
		query = self.parse_phrase(query)
		query = self.parse_boolean(query)
		return query

	def not_null(tstr):
		return tstr != ''

	def parse_wildcard(self, query):
		"""Extract wildcard queries into query{}"""
		regex = r"([\w]+)?([\*])([\w]+)?"
		query['wild'] = re.findall(regex, self.line)
		if query['wild']:
			self.line = re.sub(regex, '', self.line)
			# print(list(query['wild']))
			# print(query['wild'][0])
			for i in range(len(query['wild'])):
				query['wild'][i] = list(filter(len, query['wild'][i]))
				print(query['wild'][i])
		print(list(query['wild']))
		return query


	def parse_phrase(self, query):
		"""extract phrase query terms into query{}"""
		regex = r'\w*"([^"]*)"'
		query['phrase'] = re.findall(regex, self.line)
		if query['phrase']:
		  self.line = re.sub(regex, '', self.line)
		return query

	def parse_boolean(self, query):
		"""Consider whatever is left as boolean query terms"""
		query['bool'] = self.line.split()
		return query

	def parse_test(self):
		# line = "(walk|walked|walking) (sth|sth.|something) \boff\b"
		line = "\"发那软件诶框架热 杰赛科技\" \"个体软件看到的是了\" 城市举办还是女的说"
		line1 = "*发环境卫生健康 第八十年代农村的是 北京的紧身裤* *阿里我胃口"
		line2 = "和你说的那科看我 好空间哦我"
		result = self.parse_query(line1)
		print(result)

def main():
  myquery().parse_test()

if __name__ == '__main__':
  main()