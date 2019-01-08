"""
Reader and interpreter.

clean_words, freq_dist, and collocations:
	Tim Strehle @ https://www.strehle.de/tim/weblog/archives/2015/09/03/1569
	https://itnext.io/basics-of-text-analysis-visualization-1978de48af47


"""
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

def define_entities(raw_text):
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

def clean_words(raw_text):
	default_stopwords = set(nltk.corpus.stopwords.words('english'))

	raw_words = nltk.word_tokenize(raw_text)
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

def freq_dist(words):
	total_freqs = dict()

	fdist = nltk.FreqDist(words)
	for word, freq in fdist.most_common(30): # just common  or total?
		total_freqs[word] = freq
		#print(u'{};{}'.format(word, freq))

	return total_freqs

def collocations(words):
	bigrams =  defaultdict(int)
	bg_meas = BigramAssocMeasures()

	bi_finder = BigramCollocationFinder.from_words(words)
	bi_collocs = bi_finder.nbest(bg_meas.likelihood_ratio, 10)

	for colloc in bi_collocs:
		bigrams[colloc] += 1

	return bigrams # returns defaultdict, not dict!!!

def sentiment_analysis(raw_text):
	afinn = Afinn()
	sentiment_summary = defaultdict(int)

	sentences =[]
	raw_text.seek(0)
	for line in raw_text.readlines():
		if line != '\n':
			line = re.sub('\n', '', line)
			sentences.append(line)

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

def interrogative_freq(raw_text):
	'''
	Determine frequency of questions asked in text.
	Ref: 
		https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
		https://grammar.collinsdictionary.com/us/easy-learning/wh-words
	'''

	text = nltk.word_tokenize(raw_text)
	tagged = nltk.pos_tag(text)

	count = 0
	for word, pos in tagged:
		if pos in ['WRB', 'WP', 'WDT']:
			count += 1

	return count/len(tagged)

def expletive_freq(raw_text):
	expletives = ['fuck', 'shit', 'damn', 'bitch', 'hell', 'cunt']
	return


'''
FUTURE METHODS
	-vocab size and depth
	-textspeak score
'''


def main():
	# TODO something in here is really slow. what is it?
	# how can i optimize it?

	# TODO if system argument exists, record that file
	filename = 'mock-convo.txt'
	raw_text = open(filename, 'r') # need utf-8?

	#print(interrogative_freq(raw_text.read()))
	
	#all_words = clean_words(raw_text.read())

	e1, e2 = define_entities(raw_text)
	print(interrogative_freq(e1))

	#e1_words = clean_words(e1)
	#e2_words = clean_words(e2)

	#all_words = e1_words.copy()
	#all_words.extend(e2_words.copy()) # => content determines shapes

	# create output object
	#convo = dict()
	#convo['sentiment'] = sentiment_analysis(raw_text)

	'''
	e1_vocab = set(e1_words)
	e2_vocab = set(e2_words)
	all_vocab = set(all_words)

	shared = e1_vocab.intersection(e2_vocab) # => determines where local origin is
	e1_unique = [word for word in e1_vocab if word not in shared] # => determines where shapes spawn around local origin
	e2_unique = [word for word in e2_vocab if word not in shared] # => ""
	'''

	'''vocab_set = set(vocab)
	vocab_dict = dict()
	for i, word in enumerate(vocab_set):
		vocab_dict[word] = i
	vocab_size = len(vocab_dict)

	# TODO create bow with 2 rows, 1 per entity
	total_bow = np.zeros([1, vocab_size]) # TODO malleable for number of convos
	for word in words:
		col = int(vocab_dict[word])
		total_bow[0,col] += 1

	#print(total_bow)
	'''
	#with open('convo.pkl', 'wb') as file:
	#	pickle.dump(convo, file)

if __name__ == '__main__':
	main()

