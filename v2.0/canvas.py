'''
Contains Canvas class.
Visualizer 2.0.
011318
'''

import cairo 
import math
import pickle
import random

from convobj import Convobj

class Canvas(object):
	def __init__(self, filename, convobj):
		
		'''
		TODO
			-add noise to position of circles
			-set a seed for randomness
			-create more variance for colors
			-possible to give it different source than sentiment? they'll all be green
			-use freq_dist for placement of something
			-look into procedural generation
			-determine scale based on size of canvas
		'''
		
		# determine width and height
		self.width = convobj.e1.msg_count * 100
		self.height = convobj.e2.msg_count * 100
		
		# construct surface
		self.surface = cairo.SVGSurface('../images/' + filename + '.svg', self.width, self.height)
		cr = self.cr = cairo.Context(self.surface)
		c = self.c = convobj
		
		self.r,self.g,self.b,self.r_var,self.g_var,self.b_var = self.generate_color_scheme(self.c)
		
		self.generate_bg(self.cr)
		
		self.draw_msg_lengths(self.cr)
		self.draw_vocabs(self.cr, self.c)
		self.draw_freq_dist(self.cr)
		
		self.surface.write_to_png('../images/' + filename + '.png')
		cr.show_page()
		self.surface.finish()
		
	def circle(self, cr, center, radius):
		cr.set_line_width(9)
		cr.set_source_rgb(0.5, 0.6, 0.0)

		#cr.translate(center[0], center[1]) # or change scale between the 2 values to get ellipse
		cr.arc(center[0],center[1],radius,0,2*math.pi)
		cr.stroke_preserve()

		cr.set_source_rgba(0.3, 0.4, 0.0, 0.3)
		cr.fill()
		
	def generate_color_scheme(self, c):
		''' determine color scheme from sentiment '''
		r = c.whole.sentiment_summary['positive']
		g = c.whole.sentiment_summary['neutral']
		b = c.whole.sentiment_summary['negative']
		variance = abs(c.e1.sentiment_summary['neutral'] - c.e2.sentiment_summary['neutral'])
		r_var = r + random.uniform(0, variance)
		g_var = g + random.uniform(0, variance)
		b_var = b + random.uniform(0, variance)
		
		return r,g,b,r_var,g_var,b_var
	
	def generate_bg(self, cr):
		''' determine bg color '''
		cr.save()
		cr.set_line_width(0.01)
		cr.rectangle(0,0,self.width,self.height)
		cr.set_source_rgb(self.r,self.g,self.b)
		cr.fill()
		cr.restore()
		
	def draw_freq_dist(self, cr):
		whole_freqs = self.c.whole.freq_dist
		e1_freqs = self.c.e1.freq_dist
		e2_freqs = self.c.e2.freq_dist
		
		cr.save()
		# scale canvas to 1x1
		cr.scale(self.width, self.height)
		cr.set_source_rgba(self.g, self.b, self.r, 0.5)
		#cr.set_line_width(0.001)
		
		stretch = len(whole_freqs)
		i = 0
		for word, value in whole_freqs.items():
			x = i / stretch
			y = 0.3
			
			v2 = 1 / value
			cr.set_line_width(value / 300)
			
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
							1 - x - v3, 1 - y - v3)
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
				
		cr.restore()
				
	def draw_msg_lengths(self, cr):
		''' avg message length ''' 
		cr.save()
		cr.scale(self.width, self.height)
		hyp = self.c.whole.msg_length_avg
		std = self.c.whole.msg_length_std
		
		ctr = (1/2 + 1/self.c.e1.msg_length_avg,
			   1/2 + 1/self.c.e2.msg_length_avg)
		cr.set_source_rgb(0.0,0.1,0.0)
		cr.set_line_width(0.001)
		
		angle = (2 * math.pi) / self.c.whole.msg_count
		
		for i in range(self.c.whole.msg_count):
			theta = angle * i
			this_hyp = (1/hyp + 1/random.uniform(0, std))
			y = this_hyp * math.sin(theta)
			x = this_hyp * math.cos(theta)
			
			cr.move_to(ctr[0], ctr[1])
			cr.line_to(ctr[0] + x, ctr[1] + y)
			cr.stroke()
			
		cr.restore()
		
	def draw_vocabs(self, cr, c):
		cr.save()
		cr.scale(1,1)
		# use overall vocab size to make a clip space
		c0 = dict()
		c0['center'] = [self.width/2, self.height/2]
		c0['radius'] = c.whole.vocab_size * 10
		cr.arc(c0['center'][0], c0['center'][1], c0['radius'], 0, 2*math.pi)
		cr.set_source_rgba(self.r_var, self.g_var, self.b_var, 0.9)
		cr.fill()
		
		cr.arc(c0['center'][0], c0['center'][1], c0['radius'], 0, 2*math.pi)
		cr.clip()
		
		c1 = dict()
		c1['center'] = [self.width/3, self.height/3]
		c1['radius'] = c.e1.vocab_size * 10
		
		c2 = dict()
		c2['center'] = [2*self.width/3, 2*self.height/3]
		c2['radius'] = c.e2.vocab_size * 10
		
		self.circle(self.cr, c1['center'], c1['radius'])
		self.circle(self.cr, c2['center'], c2['radius'])
		cr.paint()
		
		cr.restore()
		

def main():
	convo = pickle.load(open('convo-matthew-w-freq.pkl', 'rb'))
	c = Canvas('layering-3', convo)
	
if __name__ == '__main__':
	main()