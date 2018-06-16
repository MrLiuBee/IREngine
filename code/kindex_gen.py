# -*- coding: utf-8 -*-

import marshal

class Kgen:

	kindex_name = "../data/kindex1.dat"

	kgrams_length = 2
	kindex = {}
	wordlist = []

	# def __init__(self, wordlist):
	# 	self.wordlist = wordlist
	# 	print(self.wordlist)

	def build_kindex(self):
		'''基于索引词项构建 k-gram 索引'''
		for w in self.wordlist:
			for g in self.kgrams(w):
				if g not in self.kindex: self.kindex[g] = set()
				self.kindex[g].add(w)

	def kgrams(self, term):
		"""Build all possible kgrams for term"""
		k = self.kgrams_length
		kgrams = ["$" + term[0:k-1]]
		for i in range(len(term) - (k-1)):
			kgrams.append(term[i:i+k])
		kgrams.append(term[-(k-1):] + "$")
		return kgrams

	def save_kindex(self):
		'''将 k-gram 索引保存到硬盘'''
		print(self.kindex)
		kgram_file = open(self.kindex_name, "wb")
		marshal.dump(self.kindex, kgram_file)
		kgram_file.close()

	def execute(self, wordlist):
		print("开始构建轮排索引...")
		self.wordlist = wordlist
		self.build_kindex()
		self.save_kindex()

		print("测试：")
		f = open("../data/kindex.dat", "rb")
		f = marshal.load(f)
		print(f)
		myword = []
		for term in f.keys():
			if "北京" == term:
				for i in f[term]:
					print(i)
					myword.append(i)
		print(myword)

def main():
	wordlist = ['思考', '北京航空', '天津之眼', '天津铁路']
	Kgen().execute(wordlist)


if __name__ == '__main__':
  main()




