# -*- coding: utf-8 -*-

import logging as mod_logging
import Image as mod_image
import ImageDraw as mod_imagedraw

import srtm as mod_srtm

mod_logging.basicConfig(level=mod_logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

geo_elevation_data = mod_srtm.get_data()

image = geo_elevation_data.get_image((500, 500), (20, 30), (-80, -70), 300)

image.show()
