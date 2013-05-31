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

"""
Classess containing parsed elevation data.
"""

import pdb

import logging as mod_logging
import math as mod_math
import re as mod_re
import urllib as mod_urllib
import os.path as mod_path
import zipfile as mod_zipfile
import cStringIO as mod_cstringio

from . import utils as mod_utils
from . import retriever as mod_retriever

class GeoElevationData:
    """
    The main class with utility methods for elevations. Note that files are 
    loaded in memory, so if you need to find elevations for multiple points on 
    the earth -- this will load *many* files in memory!
    """

    srtm1_files = None
    srtm3_files = None

    # Lazy loaded files used in current app:
    files = None

    def __init__(self, srtm1_files, srtm3_files, files_directory):
        self.srtm1_files = srtm1_files
        self.srtm3_files = srtm3_files
        # Place where local files are stored:
        self.files_directory = files_directory

        self.files = {}

    def get_elevation(self, latitude, longitude):
        geo_elevation_file = self.get_file(float(latitude), float(longitude))

        mod_logging.debug('File for ({0}, {1}) -> {2}'.format(
                          latitude, longitude, geo_elevation_file))

        if not geo_elevation_file:
            return None

        return geo_elevation_file.get_elevation(float(latitude), float(longitude))

    def get_file(self, latitude, longitude):
        """
        If the file can't be found -- it will be retrieved from the server.
        """
        file_name = self.get_file_name(latitude, longitude)
		
        if not file_name:
            return None

        if self.files.has_key(file_name):
            return self.files[file_name]
        else:
            data = self.retrieve_or_load_file_data(file_name)
            if not data:
                return None

            result = GeoElevationFile(file_name, data)
            self.files[file_name] = result
            return result

    def retrieve_or_load_file_data(self, file_name):
        data_file_name = '{0}/{1}'.format(self.files_directory, file_name)

        if mod_path.exists(data_file_name):
            f = open(data_file_name)
            data = f.read()
            f.close()

            return data

        url = None

        if self.srtm1_files.has_key(file_name):
            url = self.srtm1_files[file_name]
        elif self.srtm3_files.has_key(file_name):
            url = self.srtm3_files[file_name]

        if not url:
            mod_logging.error('No file found: {0}'.format(file_name))
            return None

        f = mod_urllib.urlopen(url)
        mod_logging.info('Retrieving {0}'.format(url))
        data = f.read()
        mod_logging.info('Retrieved {0}'.format(url))
        f.close()

        # data is zipped:
        mod_logging.info('Unzipping {0}'.format(url))
        zip_file = mod_zipfile.ZipFile(mod_cstringio.StringIO(data))
        zip_info_list = zip_file.infolist()
        zip_info = zip_info_list[0]
        data = zip_file.open(zip_info).read()
        mod_logging.info('Unzipped {0}'.format(url))

        if not data:
            return None

        f = open(data_file_name, 'w')
        f.write(data)
        f.close()

        return data

    def get_file_name(self, latitude, longitude):
        # Decide the file name:
        if latitude >= 0:
            north_south = 'N'
        else:
            north_south = 'S'

        if longitude >= 0:
            east_west = 'E'
        else:
            east_west = 'W'

        file_name = '%s%s%s%s.hgt' % (north_south, str(int(abs(mod_math.floor(latitude)))).zfill(2), 
                                      east_west, str(int(abs(mod_math.floor(longitude)))).zfill(3))

        if not self.srtm1_files.has_key(file_name) and not self.srtm3_files.has_key(file_name):
            mod_logging.debug('No file found for ({0}, {1}) (file_name: {2})'.format(latitude, longitude, file_name))
            return None

        return file_name

    def get_image(self, size, latitude_interval, longitude_interval, max_elevation, 
                  unknown_color = (255, 255, 255, 255), zero_color = (0, 0, 255, 255),
                  min_color = (0, 0, 0, 255), max_color = (0, 255, 0, 255)):
        """
        Returns a PIL image.
        """
        import Image as mod_image
        import ImageDraw as mod_imagedraw

        if not size or len(size) != 2:
            raise Exception('Invalid size %s' % size)
        if not latitude_interval or len(latitude_interval) != 2:
            raise Exception('Invalid latitude interval %s' % latitude_interval)
        if not longitude_interval or len(longitude_interval) != 2:
            raise Exception('Invalid longitude interval %s' % longitude_interval)

        width, height = size
        width, height = int(width), int(height)

        latitude_from,  latitude_to  = latitude_interval
        longitude_from, longitude_to = longitude_interval

        image = mod_image.new('RGBA', (width, height),
                              (255, 255, 255, 255))
        draw = mod_imagedraw.Draw(image)

        for row in range(height):
            for column in range(width):
                latitude  = latitude_from  + float(row) / height * (latitude_to  - latitude_from)
                longitude = longitude_from + float(column) / height * (longitude_to - longitude_from)
                elevation = self.get_elevation(latitude, longitude)

                if elevation == None:
                    color = unknown_color
                else:
                    elevation_coef = elevation / float(max_elevation)
                    if elevation_coef < 0: elevation_coef = 0
                    if elevation_coef > 1: elevation_coef = 1
                    color = mod_utils.get_color_between(min_color, max_color, elevation_coef)
                    if elevation <= 0:
                        color = zero_color

                draw.point((column, height - row), color)

        return image

class GeoElevationFile:
    """ Contains data from a single Shuttle elevation file. """

    file_name = None
    url = None
	
    latitude = None
    longitude = None

    data = None

    def __init__(self, file_name, data):
        """ Data is a raw file contents of the file. """

        self.file_name = file_name

        self.parse_file_name_starting_position()

        self.data = data

        square_side = mod_math.sqrt(len(self.data) / 2.)
        assert square_side == int(square_side), 'Invalid file size: {0} for file {1}'.format(len(self.data), self.file_name)

        self.square_side = int(square_side)

    def get_elevation(self, latitude, longitude):
        if not (self.latitude <= latitude < self.latitude + 1):
            raise Exception('Invalid latitude %s for file %s' % (latitude, self.file_name))
        if not (self.longitude <= longitude < self.longitude + 1):
            raise Exception('Invalid longitude %s for file %s' % (longitude, self.file_name))

        points = self.square_side ** 2

        pdb.set_trace()
        row = int(mod_math.floor((self.latitude + 1 - latitude) * float(self.square_side - 1)))
        column = int(mod_math.floor((longitude - self.longitude) * float(self.square_side - 1)))

        return self.get_elevation_from_row_and_column(row, column)

    def get_elevation_from_row_and_column(self, row, column):
        i = row * (self.square_side) + column
        assert i < len(self.data) - 1

        mod_logging.debug('{0}, {1} -> {2}'.format(row, column, i))

        byte_1 = ord(self.data[i * 2])
        byte_2 = ord(self.data[i * 2 + 1])

        result = byte_1 * 256 + byte_2

        if result > 9000:
            # TODO(TK) try to detect the elevation from neighbour point:
            return None

        return result

    def parse_file_name_starting_position(self):
        """ Returns (latitude, longitude) of lower left point of the file """
        groups = mod_re.findall('([NS])(\d+)([EW])(\d+)\.hgt', self.file_name)

        assert groups and len(groups) == 1 and len(groups[0]) == 4, 'Invalid file name {0}'.format(self.file_name)

        groups = groups[0]

        if groups[0] == 'N':
            latitude = float(groups[1])
        else:
            latitude = - float(groups[1])

        if groups[2] == 'E':
            longitude = float(groups[3])
        else:
            longitude = - float(groups[3])

        self.latitude = latitude
        self.longitude = longitude
	
    def __str__(self):
        return '[{0}:{1}]'.format(self.__class__, self.file_name)

