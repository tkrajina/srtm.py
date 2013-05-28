# -*- coding: utf-8 -*-

import Image as mod_image
import ImageDraw as mod_imagedraw
import srtm as mod_srtm

def get_color_between(color1, color2, i):
    """ i is a number between 0 and 1, if 0 then color1, if 1 color2, ... """
    if i <= 0:
        return color1
    if i >= 1:
        return color2
    return (int(color1[0] + (color2[0] - color1[0]) * i),
            int(color1[1] + (color2[1] - color1[1]) * i),
            int(color1[2] + (color2[2] - color1[2]) * i))

ZERO_COLOR = (0  , 0  , 255, 255)
MIN_COLOR  = (0  , 0  , 0  , 255)
MAX_COLOR  = (0  , 255, 0  , 255)

width, height = 300, 300
max_elevation = 300

start_latitude, start_longitude = 45.0, 13.0
# Zašto ovo pukne?
#start_latitude, start_longitude = 43.0, 14.0

geo_elevation_data = mod_srtm.get_data()
geo_file = geo_elevation_data.get_file(start_latitude, start_longitude)

side = geo_file.square_side

image = mod_image.new('RGBA', (side, side),
                      (255, 255, 255, 255))
draw = mod_imagedraw.Draw(image)

for row in range(side):
    if row % 100 == 0:
        print 'row=%s' % row
    for column in range(side):
        elevation = geo_file.get_elevation_from_row_and_column(row, column)

        if elevation != None:
            elevation_coef = elevation / float(max_elevation)
            if elevation_coef < 0: elevation_coef = 0
            if elevation_coef > 1: elevation_coef = 1
        else:
            elevation_coef = ZERO_COLOR

        color = get_color_between(MIN_COLOR, MAX_COLOR, elevation_coef)
        if elevation <= 0:
            color = ZERO_COLOR

        draw.point((column, row), color)

image.show()
