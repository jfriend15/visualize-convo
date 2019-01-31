'''
Runs the Visualize Conversation program

FUTURE MODS
	-https://www.stefaanlippens.net/python-pickling-and-dealing-with-attributeerror-module-object-has-no-attribute-thing.html
	 Convobj.__module__ = 'convobj' => look into this 
'''
import nltk
from os import path
import sys
import pickle
from convobj import Convobj
from canvas import Canvas

def main():

	# Uncomment on first use of program
	#nltk.download('stopwords')
	#nltk.download('punkt')
	#nltk.download('averaged_perceptron_tagger')
	#nltk.download('wordnet')

	if len(sys.argv) > 1:
		name = sys.argv[1]
	else:
		name = 'anna'

	if path.exists('pickles/' + name + '.pkl'):
		convo = pickle.load(open('pickles/' + name + '.pkl', 'rb'))
		painting = Canvas(name, convo)

	elif path.exists('../convos/' + name + '.txt'):
		convo = Convobj('../convos/' + name + '.txt')
		convo.save(name)
		painting = Canvas(name, convo)

	else:
		print('Did not locate a ' + name +  ' txt or pkl file. Please try again.')
		exit()



if __name__ == '__main__':
	main()