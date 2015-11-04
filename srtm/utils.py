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

import logging
import math
import zipfile
import io

ONE_DEGREE = 1000. * 10000.8 / 90.

def distance(latitude_1, longitude_1, latitude_2, longitude_2):
    """
    Distance between two points.
    """

    coef = math.cos(latitude_1 / 180. * math.pi)
    x = latitude_1 - latitude_2
    y = (longitude_1 - longitude_2) * coef

    return math.sqrt(x * x + y * y) * ONE_DEGREE

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
    logging.debug('Zipping %s bytes' % len(contents))
    result = io.BytesIO()
    zip_file = zipfile.ZipFile(result, 'w', zipfile.ZIP_DEFLATED, False)
    zip_file.writestr(file_name, contents)
    zip_file.close()
    result.seek(0)
    logging.debug('Zipped')
    return result.read()

def unzip(contents):
    logging.debug('Unzipping %s bytes' % len(contents))
    zip_file = zipfile.ZipFile(io.BytesIO(contents))
    zip_info_list = zip_file.infolist()
    zip_info = zip_info_list[0]
    result = zip_file.open(zip_info).read()
    logging.debug('Unzipped')
    return result
