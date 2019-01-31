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
	'''
	Object that describes a conversation between two speakers
	'''

	class Entity:
		def __init__(self, text, name='test'):
			
			'''
			Object that describes the content of a speaker in a text conversation

			FUTURE MODS
				-scale interrogativeness (how often the entity asks qs)
				 in a meaningful way
				-measure vocab "depth" (how complex the words)
				-measure expletiveness (how often does the entity swear)
			'''
			
			self.name = name

			msgs = self.clean_msgs(text)
			words = self.clean_words(msgs)

			self.msg_count = len(msgs)
			self.msg_length_avg, self.msg_length_std = self.avg_msg_length(msgs)
			self.vocab_size = len(set(words))

			self.sentiment_summary = self.sentiment_analysis(msgs)
			self.interrogativeness = self.interrogative_freq(words)
			self.freq_dist = self.freq_dist(words, max=50)


		def __iter__(self):
			for attr, value in self.__dict__.items():
				yield attr, value


		def clean_words(self, msgs):
			'''
			Returns a list of all words used by the entity.

			FUTURE MODS
				-handle textspeak e.g. u, idk
				-explore stemming
				-explore lemmatizing
				-handle contractions
			'''
			default_stopwords = set(nltk.corpus.stopwords.words('english'))

			# Retrieve all words present in messages
			raw_words = []
			for m in msgs:
				raw_words.extend(m.split(' '))
			
			# Clean those words of punctuation
			words = []
			for word in raw_words:	
				words.extend(re.findall('^[A-Za-z]+', word))

			# Make all words lowercase to condense copies later
			words = [word.lower() for word in words]

			# Remove all nltk-defined stopwards
			words = [word for word in words if word not in default_stopwords]

			return words


		def clean_msgs(self, text):
			text = text.split('\n')
			return [t for t in text if t != '']


		def avg_msg_length(self, msgs):
			'''
			Returns average message length and standard deviation
			'''
			msg_lengths = []
			for msg in msgs:
				msg_lengths.append(len(msg.split(' ')))
			mean = sum(msg_lengths)/len(msgs)	
			
			# Handle standard deviation
			for_std = [(l-mean)**2 for l in msg_lengths]
			std = math.sqrt(sum(for_std)/len(for_std))

			return mean, std


		def freq_dist(self, words, max=30):
			'''
			Returns frequency distribution of words used by entity

			FUTURE MODS
				-consider returning all of fdist instead of most common
			'''
			total_freqs = dict()

			fdist = nltk.FreqDist(words)
			for word, freq in fdist.most_common(max):
				total_freqs[word] = freq

			return total_freqs


		def collocations(self, words):
			'''
			Rerturns frequency distribution of collocations

			NOT CURRENTLY IN USE
			'''
			bigrams =  defaultdict(int)
			bg_meas = BigramAssocMeasures()

			bi_finder = BigramCollocationFinder.from_words(words)
			bi_collocs = bi_finder.nbest(bg_meas.likelihood_ratio, 10)

			for colloc in bi_collocs:
				bigrams[colloc] += 1

			return bigrams


		def interrogative_freq(self, words):
			'''
			Determines frequency of questions asked in text.

			REFS 
				-https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
				-https://grammar.collinsdictionary.com/us/easy-learning/wh-words

			NOT CURRENTLY IN USE
			'''
			tagged = nltk.pos_tag(words)

			count = 0
			for word, pos in tagged:
				if pos in ['WRB', 'WP', 'WDT']:
					count += 1

			return count/len(tagged)


		def sentiment_analysis(self, sentences, freqs=True):
			'''
			Determines sentiment score PER MESSAGE, NOT per sentence
			Scores are frequencies
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
		Differentiates words between the two speakers. Returns a string for each.
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