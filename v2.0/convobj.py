'''
Contains Convobj (Conversation-Object) class.
01082019
'''

import nltk
from nltk.corpus import stopwords
from nltk.collocations import BigramCollocationFinder, BigramAssocMeasures
from afinn import Afinn

#nltk.download('stopwords')
#nltk.download('punkt')
#nltk.download('averaged_perceptron_tagger')

from collections import defaultdict
import re
import numpy as np
import pickle

class Convobj:

	class Entity:
		def __init__(self, text, name='test'):

			self.name = name

			words = self.clean_words(text)
			msgs = self.clean_msgs(text)

			self.msg_count = len(msgs)
			self.avg_msg_length = self.avg_msg_length(msgs)
			#self.vocab_size
			#self.vocab_depth

			self.sentiment_summary = self.sentiment_analysis(msgs)
			#self.interrogativeness = self.interrogative_freq(words)
			#self.expletive_freq


		def __iter__(self):
			for attr, value in self.__dict__.items():
				yield attr, value
				

		def print(self):
			print('ENTITY', self.name)


		def clean_words(self, text):
			default_stopwords = set(nltk.corpus.stopwords.words('english'))

			raw_words = nltk.word_tokenize(text.read())
			words = [word for word in raw_words if len(word) > 1]
			words = [word.lower() for word in words]
			words = [word for word in words if word not in default_stopwords]

			'''
			TODO
				- handle textspeak e.g. u, idk
				- handle misspellings
				- look into stemming e.g. playing => play
				- handle contractions e.g. i'll => i
			'''

			return words


		def clean_msgs(self, text):
			msgs =[]
			text.seek(0)
			for line in text.readlines():
				if line != '\n':
					line = re.sub('\n', '', line)
					msgs.append(line)

			return msgs


		def avg_msg_length(self, msgs):
			'''
			Determines msg length based on number of words
			'''
			msg_lengths = []
			for msg in msgs:
				msg_lengths.append(len(msg.split(' ')))

			return sum(msg_lengths)/len(msgs)


		def freq_dist(self, words):
			total_freqs = dict()

			fdist = nltk.FreqDist(words)
			for word, freq in fdist.most_common(30): # just common  or total?
				total_freqs[word] = freq
				#print(u'{};{}'.format(word, freq))

			return total_freqs


		def collocations(self, words):
			bigrams =  defaultdict(int)
			bg_meas = BigramAssocMeasures()

			bi_finder = BigramCollocationFinder.from_words(words)
			bi_collocs = bi_finder.nbest(bg_meas.likelihood_ratio, 10)

			for colloc in bi_collocs:
				bigrams[colloc] += 1

			return bigrams # returns defaultdict, not dict!!!


		def interrogative_freq(self, words):
			'''
			Determine frequency of questions asked in text.
			Ref: 
				https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
				https://grammar.collinsdictionary.com/us/easy-learning/wh-words
			'''
			tagged = nltk.pos_tag(words)

			count = 0
			for word, pos in tagged:
				if pos in ['WRB', 'WP', 'WDT']:
					count += 1

			return count/len(tagged)


		def sentiment_analysis(self, sentences):
			'''
			Determines sentiment score PER MESSAGE, NOT per sentence
			'''
			afinn = Afinn()
			sentiment_summary = defaultdict(int)

			for sentence in sentences:
				sentiment = afinn.score(sentence)
				if sentiment == 0.0:
					sentiment_summary['neutral'] += 1
				elif sentiment > 0.0:
					sentiment_summary['positive'] += 1
				else:
					sentiment_summary['negative'] += 1

			# TODO make it work for 1 entity

			return sentiment_summary


	def __init__(self, filename):

		raw_text = open(filename, 'r')
		e1_text, e2_text = self.define_entities(raw_text)
		
		#self.e1 = self.Entity(e1_text)
		#self.e2 = self.Entity(e2_text)
		self.whole = self.Entity(raw_text)


	def define_entities(self, raw_text):
		"""
		Differentiate words between the two speakers. Returns a string for each.
		"""
		e1 = ''
		e2 = ''
		speaker = 1
		raw_text.seek(0)
		for line in raw_text.readlines():
			if line == '\n' and speaker == 1:
				speaker = 2
			elif line == '\n' and speaker == 2:
				speaker = 1
			elif speaker == 1:
				e1 += line
			else:
				e2 += line

		return e1, e2

	def save(self, filename='test'):
		with open('convo' + filename + '.pkl', 'wb') as file:
			pickle.dump(self, file)


def main():

	filename = 'mock-convo.txt'
	c = Convobj(filename)
	print(dict(c.whole))


if __name__ == '__main__':
	main()