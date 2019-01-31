'''
Helper functions.

'''
import math
import datetime
from scipy import interp, arange
from numpy import linspace

def generate_rgb(xyz):
	'''
	Create an rgb value from a list of three floats
	TODO create a function that maps more intentionally
	'''
	def map_btwn_01(x):
		freq = 1 # TODO custom freq
		return 0.5 * math.sin(freq * x) + 0.5

	return [map_btwn_01(xyz[0]), map_btwn_01(xyz[1]), map_btwn_01(xyz[2])]

#def circle_intersection(c1,c2):
#	intersections = []

def map(i, xlim, ylim=0.5):
	x = arange(xlim)
	y = linspace(0, ylim, num=xlim) # default num=50
	return interp(i, x, y)

#print(generate_rgb([16,41,8]))
#print(datetime.datetime.now().day)
print(100, map(100))
print(90, map(90))
print(10, map(10))
print(700, map(700))
