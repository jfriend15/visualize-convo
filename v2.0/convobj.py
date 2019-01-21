'''
Contains Convobj (Conversation-Object) class.
01082019
'''

import nltk
from nltk.corpus import stopwords
from nltk.collocations import BigramCollocationFinder, BigramAssocMeasures
from afinn import Afinn

from collections import defaultdict
import re
import numpy as np
import pickle
import math

class Convobj:

	class Entity:
		def __init__(self, text, name='test'):
			
			'''
			TODO
				-fix interrogativeness
			'''
			
			
			self.name = name

			msgs = self.clean_msgs(text)
			words = self.clean_words(msgs)

			self.msg_count = len(msgs)
			self.msg_length_avg, self.msg_length_std = self.avg_msg_length(msgs)
			self.vocab_size = len(set(words))
			#self.vocab_depth

			self.sentiment_summary = self.sentiment_analysis(msgs)
			self.interrogativeness = self.interrogative_freq(words)
			#self.expletive_freq
			self.freq_dist = self.freq_dist(words, max=50)


		def __iter__(self):
			for attr, value in self.__dict__.items():
				yield attr, value
				

		def print(self):
			print('ENTITY', self.name)


		def clean_words(self, msgs):
			default_stopwords = set(nltk.corpus.stopwords.words('english'))
			#lemma = nltk.wordnet.WordNetLemmatizer()

			raw_words = []
			for m in msgs:
				raw_words.extend(m.split(' '))
				
			words = []
			for word in raw_words:	
				words.extend(re.findall('^[A-Za-z]+', word))

			#words = [word for word in raw_words if len(word) > 1]
			words = [word.lower() for word in words]
			words = [word for word in words if word not in default_stopwords]
			#words = [lemma.lemmatize(word) for word in words]
			'''
			TODO
				- handle textspeak e.g. u, idk => another function
				- look into stemming e.g. playing => play
				- handle contractions e.g. i'll => i
			'''

			return words


		def clean_msgs(self, text):
			text = text.split('\n')
			return [t for t in text if t != '']


		def avg_msg_length(self, msgs):
			'''
			Determines avg += std dev msg length based on number of words
			'''
			msg_lengths = []
			for msg in msgs:
				msg_lengths.append(len(msg.split(' ')))
			mean = sum(msg_lengths)/len(msgs)	
			
			# standard deviation
			for_std = [(l-mean)**2 for l in msg_lengths]
			std = math.sqrt(sum(for_std)/len(for_std))

			return mean, std


		def freq_dist(self, words, max=30):
			total_freqs = dict()

			fdist = nltk.FreqDist(words)
			for word, freq in fdist.most_common(max): # just common  or total?
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


		def sentiment_analysis(self, sentences, freqs=True):
			'''
			Determines sentiment score PER MESSAGE, NOT per sentence.
			Scores can be frequencies.
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
			if freqs:
				sentiment_summary['neutral'] = sentiment_summary['neutral']/len(sentences)
				sentiment_summary['positive'] = sentiment_summary['positive']/len(sentences)
				sentiment_summary['negative'] = sentiment_summary['negative']/len(sentences)

			return sentiment_summary


	def __init__(self, filename):

		raw_text = open(filename, 'r')
		e1_text, e2_text = self.define_entities(raw_text)
		
		raw_text.seek(0)
		self.e1 = self.Entity(e1_text, name='e1')
		self.e2 = self.Entity(e2_text, name='e2')
		self.whole = self.Entity(raw_text.read(), name='whole')


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
		with open('convo-' + filename + '.pkl', 'wb') as file:
			pickle.dump(self, file)
		file.close()


def main():
	
	# Uncomment on first use of program
	#nltk.download('stopwords')
	#nltk.download('punkt')
	#nltk.download('averaged_perceptron_tagger')
	#nltk.download('wordnet')

	filename = 'matthew.txt'
	c = Convobj(filename)
	print(dict(c.e1))
	print(dict(c.e2))
	print(dict(c.whole))
	# https://www.stefaanlippens.net/python-pickling-and-dealing-with-attributeerror-module-object-has-no-attribute-thing.html
	#Convobj.__module__ = 'convobj' => look into this 
	c.save(filename='matthew-w-freq')


if __name__ == '__main__':
	main()