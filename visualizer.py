"""
Visualizer.

Pycairo documentation found here:
	https://pycairo.readthedocs.io/en/latest/index.html

Other resources:
	http://www.tortall.net/mu/wiki/PyGTKCairoTutorial

"""

#from PIL import Image, ImageDraw

import cairo 
import math

class Canvas(object):
	def __init__(self, filename, width, height):
		self.surface = cairo.SVGSurface('images/' + filename + '.svg', width, height)
		cr = self.cr = cairo.Context(self.surface)

		self.width = width
		self.height = height

		# to work with a 1x1 canvas
		#cr.scale(width, height) 

		# Background
		cr.save()
		self.bg(self.cr, [1, 0.7, 1])
		cr.restore()

		# Border
		'''
		cr.save()
		cr.set_line_width( max(cr.device_to_user_distance(2,2)) )
		cr.set_source_rgb(0,0,0)
		cr.rectangle(0,0,1,1)
		cr.stroke()
		cr.restore()
		'''

		cr.save()
		self.line(self.cr)
		cr.restore()

		cr.save()
		self.circle(self.cr)
		cr.restore()

		# Save
		self.surface.write_to_png('images/' + filename + '.png')
		cr.show_page()
		self.surface.finish()

	def get_size(self):
		return self.width, self.height

	def bg(self, cr, rgb):
		cr.set_line_width(0.01)
		cr.rectangle(0,0,self.width,self.height)
		cr.set_source_rgb(rgb[0],rgb[1],rgb[2])
		cr.fill()

	def line(self, cr):
		cr.set_source_rgb(0,0,0)
		cr.set_line_width(9)

		cr.move_to(.25 * self.width,.25 * self.height)
		cr.line_to(0.9 * self.width,0.9 * self.height)
		cr.stroke()

	def circle(self, cr):
		#cr.save()
		cr.set_line_width(9)
		cr.set_source_rgb(0.5, 0.6, 0.0)

		w,h = self.get_size() # check

		cr.translate(w/2, h/2)
		cr.arc(0,0,.5 * w,0,2*math.pi)
		cr.stroke_preserve()

		cr.set_source_rgba(0.3, 0.4, 0.0, 0.5)
		cr.fill()
		#cr.restore()


c = Canvas('cairo_test3', 400, 300)

'''
# Sets color and transparency
cr.set_source_rgba(r,g,b,a)

cr.move_to(0.25,0.25) # start point
cr.line_to(1,1) # end point
cr.set_line_width(0.2)
cr.stroke() # makes mark

cr.rectangle(0,0,0.5,0.5)
cr.set_source_rgba(1,0,0,0.8)
cr.fill()
'''

'''surface = cairo.SVGSurface('cairo_test.svg', 300, 300)
cr = cairo.Context(surface)

cr.set_source_rgb(0.9,0.9,0.9)
cr.paint()

x,y,w,h = 40,40,80,24

cr.set_source_rgb(0.6,0.6,0.6)
cr.rectangle(x,y,w,h)
cr.stroke()

cr.save() # necessary?
cr.set_source_rgb(.2,.3,.4)
cr.rectangle(x,y,w,h)
cr.clip()
cr.paint()
cr.restore()
'''

