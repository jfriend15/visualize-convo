"""
Reader and interpreter.

First 4 methods from:
	Tim Strehle @ https://www.strehle.de/tim/weblog/archives/2015/09/03/1569
	https://itnext.io/basics-of-text-analysis-visualization-1978de48af47


"""
import nltk
from nltk.corpus import stopwords
from nltk.collocations import BigramCollocationFinder, BigramAssocMeasures
from afinn import Afinn

#nltk.download('stopwords')
#nltk.download('punkt')

from collections import defaultdict
import re
import numpy as np

def clean_words(raw_text):
	default_stopwords = set(nltk.corpus.stopwords.words('english'))

	raw_words = nltk.word_tokenize(raw_text.read())
	words = [word for word in raw_words if len(word) > 1]
	words = [word.lower() for word in words]
	words = [word for word in words if word not in default_stopwords]

	return words

def freq_dist(words):
	total_freqs = dict()

	fdist = nltk.FreqDist(words)
	for word, freq in fdist.most_common(30): # just common  or total?
		total_freqs[word] = freq
		print(u'{};{}'.format(word, freq))

	# TODO currently keeps "'s", "'m", and "'ll." don't do that

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

	return sentiment_summary


# TODO if system argument exists, record that file
filename = 'mock-convo.txt'
raw_text = open(filename, 'r') # need utf-8?

words = clean_words(raw_text)


# create vocabulary for both people
# TODO separate vocabularies for entities
vocab_set = set(words)
vocab_dict = dict()
for i, word in enumerate(vocab_set):
	vocab_dict[word] = i
vocab_size = len(vocab_dict)

# TODO create bow with 2 rows, 1 per entity
total_bow = np.zeros([1, vocab_size]) # TODO malleable for number of convos
for word in words:
	col = int(vocab_dict[word])
	total_bow[0,col] += 1

print(total_bow)




