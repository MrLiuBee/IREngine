# -*- coding: utf-8 -*-

import jieba

class Engine:

	store = None
	query = {}

	def search(self, query):
		"""Perform any search and return results"""
		result = []
		self.query = query
		answers = wanswers = []
		answers    = self.get_boolean_answers(answers)
		answers    = self.get_phrase_answers(answers)
		# return answers
		wanswers   = self.get_wildcard_answers(wanswers)
		print("获取结果：")
		result.append(answers)
		result.append(wanswers)
		print(result)
		return result
		# if wanswers: answers.append(set.intersection(*wanswers))
		# if answers: return set.intersection(*answers)

	def get_wildcard_answers(self, answers):
		"""perform wildcard search given a list of wildcards"""
		terms = []
		kgrams = []
		print(len(self.query['wild']))
		for q in self.query['wild']:
			kgrams = self.process_wildcard(q)
			for word in kgrams:
				terms.append(word)
			# subset = self.wildcard_terms(kgrams)
			# if subset: terms.append(subset)
		print("通配符查询推出：")
		return terms

	# def wildcard_terms(self, kgrams):
	# 	"""Given a list of kgrams, return union of their terms"""
	# 	terms = set()
	# 	for g in kgrams:
	# 		inter = set()
	# 		if g in self.store.kindex:
	# 			inter = self.store.kindex[g]
	# 		if not terms: terms = inter.copy()
	# 			terms &= inter
	# 	return terms


	def process_wildcard(self, cards):
		"""Generate a wildcard's kgrams"""
		print("enter process wildcard")
		print(len(cards))
		middle = (len(cards) == 3)
		kgrams = []
		if cards[0] == '*':
			kgrams.extend(self.kgrams(cards[1], 'end'))
		elif cards[1] == '*' and middle:
			kgrams.extend(self.kgrams(cards[0], 'start'))
			kgrams.extend(self.kgrams(cards[2], 'end'))
		else:
			kgrams.extend(self.kgrams(cards[0], 'start'))
		return kgrams

	def kgrams(self, term, pos):
		"""Generate kgrams for wildcard subset"""
		# k = self.store.kgrams_length
		k = 2
		kgrams = []
		if pos == 'start':
			kgrams.append("$" + term[0:k-1])

		for i in range(len(term) - (k-1)):
			kgrams.append(term[i:i+k])

		if pos == 'end':
			kgrams.append(term[-(k-1):] + "$")
		return [t for t in kgrams if len(t) == k]

		# for card in terms:
		# 	subset = set()
		# 	for t in card:
		# 		results = set(self.store.index[t].keys())
		# 		if not subset: subset = results.copy()
		# 		subset |= results
		# 	answers.append(subset)
		# return answers


	def get_boolean_answers(self, answers):
		"""Get boolean answers and append them to the overall list of answers"""
		if self.query["bool"]:
			for sentence in self.query["bool"]:
				boolist = jieba.lcut(sentence, cut_all = False)
				for term in boolist:
					answers.append(term)
		return answers

	def get_phrase_answers(self, answers):
		"""Get phrase answers and append them to the overall list of answers"""
		if self.query["phrase"]:
			for phrase in self.query["phrase"]:
				phlist = jieba.lcut(phrase, cut_all = False)
				for term in phlist:
					answers.append(term)
		return answers

	def parse_test(self):
		# line = "(walk|walked|walking) (sth|sth.|something) \boff\b"
		line = {'phrase': ['发那软件诶框架热 杰赛科技', '个体软件看到的是了'], 'bool': ['城市举办还是女的说'], 'wild': []}
		line1 = {'phrase': [], 'wild': [['*', '发环境卫生健康'], ['北京的紧身裤', '*'], ['*', '阿里我胃口']], 'bool': ['如何解决俄卡的紧身裤']}
		line2 = {'phrase': [], 'bool': ['和你说的那科看我', '好空间哦我'], 'wild': []}
		result = self.search(line1)
		print(result)

def main():
  Engine().parse_test()

if __name__ == '__main__':
  main()


