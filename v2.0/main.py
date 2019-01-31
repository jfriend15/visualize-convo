'''
Runs the Visualize Conversation program

FUTURE MODS
	-https://www.stefaanlippens.net/python-pickling-and-dealing-with-attributeerror-module-object-has-no-attribute-thing.html
	 Convobj.__module__ = 'convobj' => look into this 
'''
import nltk
from os import path
import sys
from convobj import Convobj

def main():

	# Uncomment on first use of program
	#nltk.download('stopwords')
	#nltk.download('punkt')
	#nltk.download('averaged_perceptron_tagger')
	#nltk.download('wordnet')

	if sys.argv[0]:
		name = sys.argv[0]
	else:
		name = 'mock-convo' # TODO allow user input
	
	filename = name + '.txt'

	if path.exists('pickles/' + name + '.pkl'):
		convo = pickle.load(open('pickles/' + name + '.pkl', 'rb'))
	elif path.exists('../convos/' + name + '.txt'):
		convo = Convobj('../convos/' + name + '.txt')
		convo.save(name)
	else:
		print('Could not find file. Please try again.')
		end()

	painting = Canvas(name, convo)


if __name__ == '__main__':
	main()