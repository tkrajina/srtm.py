# -*- coding: utf-8 -*-

# Copyright 2013 Tomo Krajina
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pdb

import logging    as mod_logging
import math       as mod_math
import zipfile    as mod_zipfile

try:
    from StringIO import cStringIO
except ImportError: # assume this is Python 3
    from io import BytesIO as cStringIO # looks hacky but we are working with bytes

ONE_DEGREE = 1000. * 10000.8 / 90.

def distance(latitude_1, longitude_1, latitude_2, longitude_2):
    """
    Distance between two points.
    """

    coef = mod_math.cos(latitude_1 / 180. * mod_math.pi)
    x = latitude_1 - latitude_2
    y = (longitude_1 - longitude_2) * coef

    return mod_math.sqrt(x * x + y * y) * ONE_DEGREE

def get_color_between(color1, color2, i):
    """ i is a number between 0 and 1, if 0 then color1, if 1 color2, ... """
    if i <= 0:
        return color1
    if i >= 1:
        return color2
    return (int(color1[0] + (color2[0] - color1[0]) * i),
            int(color1[1] + (color2[1] - color1[1]) * i),
            int(color1[2] + (color2[2] - color1[2]) * i))

def zip(contents, file_name):
    mod_logging.debug('Zipping %s bytes' % len(contents))
    result = cStringIO()
    zip_file = mod_zipfile.ZipFile(result, 'w', mod_zipfile.ZIP_DEFLATED, False)
    zip_file.writestr(file_name, contents)
    zip_file.close()
    result.seek(0)
    mod_logging.debug('Zipped')
    return result.read()

def unzip(contents):
    mod_logging.debug('Unzipping %s bytes' % len(contents))
    zip_file = mod_zipfile.ZipFile(cStringIO(contents))
    zip_info_list = zip_file.infolist()
    zip_info = zip_info_list[0]
    result = zip_file.open(zip_info).read()
    mod_logging.debug('Unzipped')
    return result
