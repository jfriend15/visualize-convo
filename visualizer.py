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
import pickle

import reader
import helper

class Canvas(object):
	def __init__(self, filename, convobj, width, height):
		self.surface = cairo.SVGSurface('images/' + filename + '.svg', width, height)
		cr = self.cr = cairo.Context(self.surface)

		self.width = width
		self.height = height

		temp = [convobj['sentiment']['positive'], convobj['sentiment']['neutral'], convobj['sentiment']['negative']]

		# to work with a 1x1 canvas
		#cr.scale(width, height) 

		# Background
		cr.save()
		#self.bg(self.cr, [1, 0.7, 1])
		self.bg(self.cr, helper.generate_rgb(temp))
		cr.restore()

		cr.save()
		self.line(self.cr)
		cr.restore()

		cr.save()
		self.circle(self.cr)
		cr.restore()

		cr.save()
		self.rectangle(self.cr)
		cr.restore()

		cr.save()
		self.bezier(self.cr)
		cr.restore()

		#cr.save()
		#self.pat(self.cr)
		#cr.restore()

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
		cr.set_dash([5, 15, 2]) # [on, off, on]
		#cr.set_line_cap(cairo.LINE_CAP_SQUARE) # or BUTT, ROUND

		cr.move_to(.25 * self.width,.25 * self.height)
		cr.line_to(0.9 * self.width,0.9 * self.height)
		cr.stroke()

	def rectangle(self, cr):
		cr.set_line_width(10)
		cr.set_source_rgba(.3,.3,0,0.6)
		cr.set_line_join(cairo.LINE_JOIN_BEVEL)
		cr.rectangle(20,20,100,200)
		cr.stroke()

	def circle(self, cr):
		#cr.save()
		cr.set_line_width(9)
		cr.set_source_rgb(0.5, 0.6, 0.0)

		w,h = self.get_size() # check

		cr.translate(w/2, h/2) # or change scale between the 2 values to get ellipse
		cr.arc(0,0,.5 * w,0,2*math.pi)
		cr.stroke_preserve()

		cr.set_source_rgba(0.3, 0.4, 0.0, 0.5)
		cr.fill()
		#cr.restore()

	def bezier(self, cr):
		cr.move_to(30,30)
		cr.curve_to(320, 200, 330, 110, 50, 40)
		cr.stroke()

	# for complex shapes, successively move_to and curve_to next
	# point in an array of points

	def pat(self, cr):
		sr1 = cairo.ImageSurface.create_from_png("pat-ex.png")
		pt1 = cairo.SurfacePattern(sr1)
		pt1.set_extend(cairo.EXTEND_REPEAT)

		cr.set_source(pt1)
		cr.rectangle(50,70,200,200)
		cr.fill()

def main():
	reader.main()
	convo = pickle.load(open('convo.pkl', 'rb'))
	print(convo['sentiment'])
	c = Canvas('cairo_test_integrate_1', convo, 400, 300)

if __name__ == '__main__':
	main()



