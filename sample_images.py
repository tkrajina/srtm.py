# -*- coding: utf-8 -*-

import logging as mod_logging
import Image as mod_image
import ImageDraw as mod_imagedraw

import srtm as mod_srtm

"""
mod_logging.basicConfig(level=mod_logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
"""

geo_elevation_data = mod_srtm.get_data()

image = geo_elevation_data.get_image((400, 400), (45, 46), (13, 14), 300)
image.save('istra.png')

miami = (25.787676, -80.224145)
image = geo_elevation_data.get_image((400, 400),
                                     (miami[0] - 1, miami[0] + 1.5),
                                     (miami[1] - 2, miami[1] + 0.5),
                                     40)
image.save('miami.png')

rio_de_janeiro = (-22.908333, -43.196389)
image = geo_elevation_data.get_image((400, 400),
                                     (rio_de_janeiro[0] - 0.5, rio_de_janeiro[0] + 2),
                                     (rio_de_janeiro[1] - 0.5, rio_de_janeiro[1] + 2),
                                     1000)
image.save('rio.png')

sidney = (-33.859972, 151.211111)
image = geo_elevation_data.get_image((400, 400),
                                     (sidney[0] - 1.5, sidney[0] + 1),
                                     (sidney[1] - 1.5, sidney[1] + 1),
                                     1000)
image.save('sidney.png')

