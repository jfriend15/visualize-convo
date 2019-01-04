"""
Visualizer.

"""

from PIL import Image, ImageDraw

#from gi.repository import Gtk
import cairo 
import gtk

im = Image.new('RGB', (100,200), (255,0,0))
dr = ImageDraw.Draw(im)

dr.rectangle(((0,0), (10,10)), fill='black', outline='blue')

#im.show("Rectangle")
#im.save("rectangle.png")