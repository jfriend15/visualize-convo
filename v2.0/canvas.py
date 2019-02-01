'''
Contains Canvas class.
Visualizer 2.0.
011318
'''

import cairo 
import math
import pickle
import random
import datetime
from scipy import interp, arange
from numpy import linspace

from convobj import Convobj

class Canvas(object):
	
	NOISE = 10 # at 1, no noise
	SIZE = 20 # controls size of canvas 
	MAX_VOCAB_SIZE = 300
	MAX_MSG_VAR = 20 # how much msg length can vary between the two entities
	MAX_WORD_FREQ = 20 # how many times a word is mentioned

	def __init__(self, filename, convobj):
		
		'''
		TODO
			-add noise to position of circles
			-set a seed for randomness
			-look into procedural generation
		'''
		
		# Determine width and height
		self.width = convobj.e1.msg_count * Canvas.SIZE
		self.height = convobj.e2.msg_count * Canvas.SIZE
		
		# Construct surface
		self.surface = cairo.SVGSurface('../images/svgs/' + filename + '.svg', self.width, self.height)
		cr = self.cr = cairo.Context(self.surface)
		c = self.c = convobj
		
		# Paint
		self.pos, self.neu, self.neg = self.generate_color_scheme(self.c)
		
		self.generate_bg(self.cr)
		
		self.draw_msg_lengths(self.cr)
		self.draw_vocabs(self.cr, self.c)
		self.draw_freq_dist(self.cr)
		
		# Save
		t = datetime.datetime.now()
		self.surface.write_to_png('../images/' + filename +
								  '-' + str(t.month) + str(t.day) + str(t.hour) + str(t.minute) +
								  '.png')
		
		cr.show_page()
		self.surface.finish()		

	
	def map(self, i, xlim, ylim=0.5, yst=0):
		''' Helper function used for mapping values to canvas's coordinates '''
		x = arange(xlim)
		y = linspace(yst, ylim, num=xlim)
		return interp(i, x, y)

		
	def generate_color_scheme(self, c, test=False):
		''' 
		Determine color scheme from text sentiment
		
		FUTURE MODS
			-create more complex color scheme
		 '''
		
		def generate_analagous(color):
			''' NOT CURRENTLY IN USE '''
			variance = Canvas.NOISE * (c.e1.sentiment_summary['neutral'] - c.e2.sentiment_summary['neutral'])
			return color + random.uniform(-variance, variance)
		
		pos = c.whole.sentiment_summary['positive']
		neu = c.whole.sentiment_summary['neutral']
		neg = c.whole.sentiment_summary['negative']
		
		'''pos_var = generate_analagous(pos)
		neu_var = generate_analagous(neu)
		neg_var = generate_analagous(neg)'''
		
		'''if test:
			self.cr.save()
			for color in [pos, neu, neg]:
				self.cr.set_source_rgb(color,0,0)
				move_to()'''
		
		return pos, neu, neg
	

	def generate_bg(self, cr):
		''' Determine background color '''
		cr.save()
		cr.set_line_width(0.01)
		cr.rectangle(0,0,self.width,self.height)
		cr.set_source_rgb(self.neg,self.neu,self.pos)
		cr.fill()
		cr.restore()
		

	def draw_freq_dist(self, cr):
		'''
		Draw "freely" based on coordinates mapped from word frequencies

		FUTURE MODS
			-look into wrapping lines around canvas
		'''
		whole_freqs = self.c.whole.freq_dist
		e1_freqs = self.c.e1.freq_dist
		e2_freqs = self.c.e2.freq_dist
		freq_size = len(whole_freqs)
		
		cr.save()
		cr.scale(self.width, self.height)
		
		for word, value in whole_freqs.items():
			start = (random.uniform(-0.05,1.05), random.uniform(-0.05,1.05))
			cr.move_to(start[0], start[1])

			# Determine end point 
			w_val = self.map(value, Canvas.MAX_WORD_FREQ) # xlim may be too big
			cr.set_line_width(self.map(value, Canvas.MAX_WORD_FREQ, ylim=0.1))
			end = (start[0] + w_val, start[1] + w_val)

			# Retrieve value from each entity for the word if it exists
			try:
				e1_val = self.map(e1_freqs[word], freq_size)
			except KeyError:
				e1_val = None
				
			try:
				e2_val = self.map(e2_freqs[word], freq_size)
			except KeyError:
				e2_val = None
			
			cr.set_source_rgba(self.neu, self.neg, self.pos, 0.4)

			# If 2 available values, draw a curve
			if e1_val and e2_val:
				mdpt1 = (start[0] + random.choice([e1_val, -1 * e1_val]), 
						1 - start[1] + random.choice([e2_val, -1 * e2_val]))
				mdpt2 = (1 - start[0] + random.choice([e1_val, -1 * e2_val]), 
						start[1] + random.choice([-1 * e1_val, e2_val]))
				cr.curve_to(mdpt1[0], mdpt1[1],
							mdpt2[0], mdpt2[1],
							end[0], end[1])
				cr.stroke()

			# Else, move start position and draw a line
			elif e1_val:
				cr.move_to(start[0], e1_val)
				cr.line_to(end[0], end[1])
				cr.stroke()

			elif e2_val:
				cr.move_to(e2_val, start[1])
				cr.line_to(end[0], end[1])
				cr.stroke()

		cr.restore()
				

	def draw_msg_lengths(self, cr):
		''' Draw radial lines based on message lengths ''' 
		cr.save()
		cr.scale(self.width, self.height)
		hyp = self.c.whole.msg_length_avg
		std = self.c.whole.msg_length_std
		
		# Determine how closely msg length compares between entities
		msg_length_diff = self.c.e2.msg_length_avg - self.c.e1.msg_length_avg

		# Determine center by
		# 1) Map the difference in msg lengths +- standard deviation to range of 
		#    [0, 1/2] where the max input value is 10 (guess)
		# 2) Repeat for each entity
		# 3) Add values to offset center at (1/2, 1/2)
		c0 = self.map(msg_length_diff + self.c.e1.msg_length_std, Canvas.MAX_MSG_VAR) # * random.choice([-1,1]), 10)
		c1 = self.map(msg_length_diff + self.c.e2.msg_length_std, Canvas.MAX_MSG_VAR) # * random.choice([-1,1]), 10)
		ctr = (1/2 + c0 * random.choice([-1,1]), 
			1/2 + c1 * random.choice([-1,1]))
		cr.set_source_rgba(self.pos,0,self.neg, 0.6)
		cr.set_line_width(0.005)
		
		angle = (2 * math.pi) / self.c.whole.msg_count
		for i in range(self.c.whole.msg_count):
			theta = angle * i / random.uniform(-std, std)
			this_hyp = (1/hyp + 1 / random.uniform(-std, std))
			y = this_hyp * math.sin(theta)
			x = this_hyp * math.cos(theta)
			
			cr.move_to(ctr[0] + 0.3 * x, ctr[1] + 0.3 * y)
			cr.line_to(ctr[0] + x, ctr[1] + y)
			cr.stroke()
			
		cr.restore()
		

	def draw_vocabs(self, cr, c):
		''' Paint overlapping circles based on vocabularies '''
		cr.save()
		cr.scale(self.width,self.height)
		
		# Use overall vocab size to make a clip space
		r0 = self.map(c.whole.vocab_size, Canvas.MAX_VOCAB_SIZE)
		cr.set_line_width(1/Canvas.MAX_VOCAB_SIZE)
		cr.set_source_rgba(self.pos, 0, 0, 0.4)
		cr.arc(1/2, 1/2, r0, 0, 2*math.pi)
		cr.stroke_preserve()
		cr.fill()
		#cr.arc(1/2, 1/2, r0, 0, 2*math.pi)
		#cr.clip()
		
		# Paint circles from individual vocab sizes in clip space
		r1 = self.map(c.e1.vocab_size, Canvas.MAX_VOCAB_SIZE)
		cr.set_source_rgb(self.neu, 0, 0)
		cr.arc(1/3, 1/3, r1, 0, 2*math.pi)
		cr.stroke_preserve()
		cr.set_source_rgba(self.neg, self.pos, 0, 0.4)
		cr.fill()
		
		r2 = self.map(c.e2.vocab_size, Canvas.MAX_VOCAB_SIZE)
		cr.set_source_rgb(self.neu, 0, 0)
		cr.arc(2/3, 2/3, r2, 0, 2*math.pi)
		cr.stroke_preserve()
		cr.set_source_rgba(self.neg, self.pos, 0, 0.4)
		cr.fill()
		
		#cr.paint()
		cr.restore()
		
# For testing purposes 
'''def main():
	convo = pickle.load(open('pickles/jacob.pkl', 'rb'))
	c = Canvas('freq-tweak-choice', convo)
	
if __name__ == '__main__':
	main()'''