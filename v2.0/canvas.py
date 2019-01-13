'''
Contains Canvas class.
Visualizer 2.0.
011318
'''

import cairo 
import math
import pickle

from convobj import Convobj

class Canvas(object):
	def __init__(self, filename, convobj):
		
		'''
		TODO
			-add noise to position of circles
		'''
		
		# determine width and height
		self.width = convobj.e1.msg_count * 100
		self.height = convobj.e2.msg_count * 100
		
		# construct surface
		self.surface = cairo.SVGSurface('../images/' + filename + '.svg', self.width, self.height)
		cr = self.cr = cairo.Context(self.surface)
		c = self.c = convobj
		
		# determine bg color
		cr.save()
		cr.set_line_width(0.01)
		cr.rectangle(0,0,self.width,self.height)
		cr.set_source_rgb(0,0.5,0.5)
		cr.fill()
		cr.restore()
		
		# draw shapes
		# vocab size
		cr.save()
		
		# use overall vocab size to make a clip space
		c0 = dict()
		c0['center'] = [self.width/2, self.height/2]
		c0['radius'] = c.whole.vocab_size * 10
		cr.arc(c0['center'][0], c0['center'][1], c0['radius'], 0, 2*math.pi)
		cr.set_source_rgba(0.8, 0.2, 0.0, 0.9)
		#cr.stroke_preserve()
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
		
		# draw lines
		
		# layer color
		
		self.surface.write_to_png('../images/' + filename + '.png')
		cr.show_page()
		self.surface.finish()
		
	def circle(self, cr, center, radius):
		cr.set_line_width(9)
		cr.set_source_rgb(0.5, 0.6, 0.0)

		#cr.translate(center[0], center[1]) # or change scale between the 2 values to get ellipse
		cr.arc(center[0],center[1],radius,0,2*math.pi)
		cr.stroke_preserve()

		cr.set_source_rgba(0.3, 0.4, 0.0, 0.5)
		cr.fill()
		

		
def main():
	convo = pickle.load(open('convo-test.pkl', 'rb'))
	c = Canvas('integrate-test-3', convo)
	
if __name__ == '__main__':
	main()