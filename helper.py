'''
Helper functions.

'''
import math

def generate_rgb(xyz):
	'''
	Create an rgb value from a list of three floats
	'''
	def map_btwn_01(x):
		freq = 1 # TODO custom freq
		return 0.5 * math.sin(freq * x) + 0.5

	return [map_btwn_01(xyz[0]), map_btwn_01(xyz[1]), map_btwn_01(xyz[2])]


#print(generate_rgb([16,41,8]))