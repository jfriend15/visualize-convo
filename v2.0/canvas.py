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
	
	def __init__(self, filename, convobj):
		
		'''
		TODO
			-add noise to position of circles
			-set a seed for randomness
			-create more variance for colors
			-possible to give it different source than sentiment? they'll all be green
			-look into procedural generation
			-determine scale based on size of canvas
		'''
		
		# determine width and height
		self.width = convobj.e1.msg_count * Canvas.SIZE
		self.height = convobj.e2.msg_count * Canvas.SIZE
		
		# construct surface
		self.surface = cairo.SVGSurface('../images/' + filename + '.svg', self.width, self.height)
		cr = self.cr = cairo.Context(self.surface)
		c = self.c = convobj
		
		self.pos, self.neu, self.neg = self.generate_color_scheme(self.c)
		
		self.generate_bg(self.cr)
		
		self.draw_msg_lengths(self.cr)
		self.draw_vocabs(self.cr, self.c)
		self.draw_freq_dist(self.cr)
		
		t = datetime.datetime.now()
		self.surface.write_to_png('../images/' + filename +
								  '-' + str(t.month) + str(t.day) + str(t.hour) + str(t.minute) +
								  '.png')
		
		cr.show_page()
		self.surface.finish()		

	
	def map(self, i, xlim, ylim=0.5, yst=0):
		x = arange(xlim)
		y = linspace(yst, ylim, num=xlim)
		return interp(i, x, y)

		
	def generate_color_scheme(self, c, test=False):
		''' determine color scheme from sentiment '''
		
		def generate_analagous(color):
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
		''' determine bg color '''
		cr.save()
		cr.set_line_width(0.01)
		cr.rectangle(0,0,self.width,self.height)
		cr.set_source_rgba(self.pos,self.neu,self.neg, 0.5)
		cr.fill()
		cr.restore()
		

	def draw_freq_dist(self, cr):
		whole_freqs = self.c.whole.freq_dist
		e1_freqs = self.c.e1.freq_dist
		e2_freqs = self.c.e2.freq_dist
		freq_size = len(whole_freqs)
		
		cr.save()
		# scale canvas to 1x1
		#cr.scale(freq_size, freq_size)
		cr.scale(self.width, self.height)
		cr.set_source_rgba(self.neu, self.neg, self.pos, 0.5)
		
		i = 0
		px = -1
		for word, value in whole_freqs.items():
			# x position alternates sides from center
			if px > 0:
				x = 1/2 + self.map(i, freq_size) * -1
			else:
				x = 1/2 + self.map(i, freq_size) 
			# y position is arbitrarily chosen
			y = 0.2
			
			v2 = 1 / value
			cr.set_line_width(value / 100)
			
			# Retrieve value from each entity for the word if it exists
			try:
				v1 = 1 / e1_freqs[word]
			except KeyError:
				v1 = None
				
			try:
				v3 = 1 / e2_freqs[word]
			except KeyError:
				v3 = None
			
			if v1 and v3:
				cr.move_to(x,y)
				cr.curve_to(x + v1, y + v1,
							x + v1 + v2, y + v1 + v2,
							1- x - v3, 1 - y - v3)
				cr.stroke()
			elif v1:
				cr.move_to(x + v1, y + v1)
				cr.line_to(x + v2, y + v2)
				cr.stroke()
			elif v3:
				cr.move_to(x + v2, y + v2)
				cr.line_to(1 - (x + v3), 1 - (x + v3))
				cr.stroke()
				
			i += 1 
			px = x # keep prev x to check identity
				
		cr.restore()
				

	def draw_msg_lengths(self, cr):
		''' avg message length ''' 
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
		cr.save()
		cr.scale(self.width,self.height)
		
		# Use overall vocab size to make a clip space
		r0 = self.map(c.whole.vocab_size, Canvas.MAX_VOCAB_SIZE)
		cr.set_line_width(1/Canvas.MAX_VOCAB_SIZE)
		cr.set_source_rgba(0, self.neu, 0, 0.7)
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
		cr.set_source_rgba(self.neu, self.neg, 0, 0.3)
		cr.fill()
		
		r2 = self.map(c.e2.vocab_size, Canvas.MAX_VOCAB_SIZE)
		cr.set_source_rgb(self.neu, 0, 0)
		cr.arc(2/3, 2/3, r2, 0, 2*math.pi)
		cr.stroke_preserve()
		cr.set_source_rgba(self.neu, self.neg, 0, 0.3)
		cr.fill()
		
		#cr.paint()
		cr.restore()
		

def main():
	convo = pickle.load(open('convo-anna-w-freq.pkl', 'rb'))
	c = Canvas('freq-scale-change', convo)
	
if __name__ == '__main__':
	main()