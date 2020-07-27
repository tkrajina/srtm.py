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
Classes containing parsed elevation data.
"""

import logging as mod_logging
import math as mod_math
import re as mod_re
import struct as mod_struct
import requests as mod_requests

from . import utils as mod_utils

from typing import *

class GeoElevationData:
    """
    The main class with utility methods for elevations. Note that files are
    loaded in memory, so if you need to find elevations for multiple points on
    the earth -- this will load *many* files in memory!
    """

    def __init__(self, srtm1_files: Dict[str, str], srtm3_files: Dict[str, str], file_handler: mod_utils.FileHandler,
                 leave_zipped: bool=False, batch_mode: bool=False, timeout: int = 0) -> None:
        self.srtm1_files = srtm1_files
        self.srtm3_files = srtm3_files
        self.leave_zipped = leave_zipped
        self.file_handler = file_handler # TODO: file_handler mypy
        self.timeout = timeout

        # Lazy loaded files used in current app:
        self.files: Dict[str, GeoElevationFile] = {}

        self.batch_mode = batch_mode

    def get_elevation(self, latitude: float, longitude: float, approximate: bool=False) -> Optional[float]:
        geo_elevation_file = self.get_file(float(latitude), float(longitude))

        #mod_logging.debug('File for ({0}, {1}) -> {2}'.format(
        #                  latitude, longitude, geo_elevation_file))

        if not geo_elevation_file:
            return None

        return geo_elevation_file.get_elevation(float(latitude), float(longitude), approximate)

    def _IDW(self, latitude: float, longitude: float, radius: float=1) -> Optional[float]:
        """
        Return the interpolated elevation at a point.

        Load the correct tile for latitude and longitude given.
        If the tile doesn't exist, return None. Otherwise,
        call the tile's Inverse Distance Weighted function and
        return the elevation.

        Args:
            latitude: float with the latitude in decimal degrees
            longitude: float with the longitude in decimal degrees
            radius: int of 1 or 2 indicating the approximate radius
                of adjacent cells to include

        Returns:
            a float of the interpolated elevation with the same unit
            as the .hgt file (meters)

        """
        tile = self.get_file(latitude, longitude)
        if tile is None:
            return None
        return tile._InverseDistanceWeighted(latitude, longitude, radius)

    def get_file(self, latitude: float, longitude: float) -> Optional["GeoElevationFile"]:
        """
        If the file can't be found -- it will be retrieved from the server.
        """
        file_name = self.get_file_name(latitude, longitude)

        if not file_name:
            return None

        if (file_name in self.files):
            return self.files[file_name]
        else:
            data = self.retrieve_or_load_file_data(file_name)
            if not data:
                return None

            result = GeoElevationFile(file_name, data, self)

            # Store file (if in batch mode, just keep most recent)
            if self.batch_mode:
                self.files = {file_name: result}
            else:
                self.files[file_name] = result

            return result

    def retrieve_or_load_file_data(self, file_name: str) -> Optional[bytes]:
        data_file_name = file_name
        zip_data_file_name = '{0}.zip'.format(file_name)

        data: Optional[bytes] = None
        if self.file_handler.exists(data_file_name):
            return self.file_handler.read(data_file_name)
        elif self.file_handler.exists(zip_data_file_name):
            byts = self.file_handler.read(zip_data_file_name)
            return mod_utils.unzip(byts)

        url = None

        if (file_name in self.srtm1_files):
            url = self.srtm1_files[file_name]
        elif (file_name in self.srtm3_files):
            url = self.srtm3_files[file_name]

        if not url:
            #mod_logging.error('No file found: {0}'.format(file_name))
            return None

        try:
            r = mod_requests.get(url, timeout=self.timeout or mod_utils.DEFAULT_TIMEOUT)
        except mod_requests.exceptions.Timeout:
            raise Exception('Connection to %s failed (timeout)' % url)
        if r.status_code < 200 or 300 <= r.status_code:
            raise Exception('Cannot retrieve %s' % url)
        mod_logging.info('Retrieving {0}'.format(url))
        data = r.content
        mod_logging.info('Retrieved {0} ({1} bytes)'.format(url, len(data)))

        if not data:
            return None

        # data is zipped:

        if self.leave_zipped:
            self.file_handler.write(data_file_name + '.zip', data)
            data = mod_utils.unzip(data)
        else:
            data = mod_utils.unzip(data)
            self.file_handler.write(data_file_name, data)

        return data

    def get_file_name(self, latitude: float, longitude: float) -> Optional[str]:
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

        if not (file_name in self.srtm1_files) and not (file_name in self.srtm3_files):
            #mod_logging.debug('No file found for ({0}, {1}) (file_name: {2})'.format(latitude, longitude, file_name))
            return None

        return file_name

    def get_image(self, size: Tuple[int, int], latitude_interval: Tuple[float, float], longitude_interval: Tuple[float, float], max_elevation: float, min_elevation: float=0,
                  unknown_color: mod_utils.Color = mod_utils.Color(255, 255, 255, 255), zero_color: mod_utils.Color = mod_utils.Color(0, 0, 255, 255),
                  min_color: mod_utils.Color = mod_utils.Color(0, 0, 0, 255), max_color: mod_utils.Color = mod_utils.Color(0, 255, 0, 255),
                  mode: str='image') -> Any:
        """
        Returns a numpy array or PIL image.
        """

        if not size or len(size) != 2:
            raise Exception('Invalid size %s' % (size, ))
        if not latitude_interval or len(latitude_interval) != 2:
            raise Exception('Invalid latitude interval %s' % (latitude_interval, ))
        if not longitude_interval or len(longitude_interval) != 2:
            raise Exception('Invalid longitude interval %s' % (longitude_interval, ))

        width, height = size
        width, height = int(width), int(height)

        latitude_from,  latitude_to  = latitude_interval
        longitude_from, longitude_to = longitude_interval


        if mode == 'array':
            import numpy as np # type: ignore
            array = np.empty((height,width))
            for row in range(height):
                for column in range(width):
                    latitude  = latitude_from  + float(row) / height * (latitude_to  - latitude_from)
                    longitude = longitude_from + float(column) / width * (longitude_to - longitude_from)
                    elevation = self.get_elevation(latitude, longitude)
                    array[row,column] = elevation

            return array

        elif mode == 'image':
            try:    import Image as mod_image # type: ignore
            except: from PIL import Image as mod_image # type: ignore
            try:    import ImageDraw as mod_imagedraw # type: ignore
            except: from PIL import ImageDraw as mod_imagedraw

            image = mod_image.new('RGBA', (width, height),
                              (255, 255, 255, 255))
            draw = mod_imagedraw.Draw(image)

            max_elevation -= min_elevation

            for row in range(height):
                for column in range(width):
                    latitude  = latitude_from  + float(row) / height * (latitude_to  - latitude_from)
                    longitude = longitude_from + float(column) / width * (longitude_to - longitude_from)
                    elevation = self.get_elevation(latitude, longitude)
                    if elevation == None:
                        color = unknown_color
                    else:
                        elevation_coef = ((elevation or 0) - (min_elevation or 0)) / float(max_elevation)
                        if elevation_coef < 0: elevation_coef = 0
                        if elevation_coef > 1: elevation_coef = 1
                        color = mod_utils.get_color_between(min_color, max_color, elevation_coef)
                        if (elevation or 0) <= 0:
                            color = zero_color
                    draw.point((column, height - row), color)

            return image
        else:
            raise Exception('Invalid mode ' + mode)

    def add_elevations(self, gpx: Any, only_missing: bool=False, smooth: bool=False, gpx_smooth_no: int=0) -> None:
        """
        only_missing -- if True only points without elevation will get a SRTM value

        smooth -- if True interpolate between points

        if gpx_smooth_no > 0 -- execute gpx.smooth(vertical=True)
        """
        if only_missing:
            original_elevations = list(map(lambda point: point.elevation, gpx.walk(only_points=True))) # type: ignore

        if smooth:
            self._add_sampled_elevations(gpx)
        else:
            for point in gpx.walk(only_points=True):
                ele = self.get_elevation(point.latitude, point.longitude)
                if ele is not None:
                    point.elevation = ele

        for i in range(gpx_smooth_no):
            gpx.smooth(vertical=True, horizontal=False)

        if only_missing:
            for original_elevation, point in zip(original_elevations, list(gpx.walk(only_points=True))):
                if original_elevation != None:
                    point.elevation = original_elevation

    def _add_interval_elevations(self, gpx: Any, min_interval_length: int=100) -> None:
        """
        Adds elevation on points every min_interval_length and add missing
        elevation between
        """
        for track in gpx.tracks:
            for segment in track.segments:
                last_interval_changed = 0
                previous_point = None
                length = 0
                for no, point in enumerate(segment.points):
                    if previous_point:
                        length += point.distance_2d(previous_point)

                    if no == 0 or no == len(segment.points) - 1 or length > last_interval_changed:
                        last_interval_changed += min_interval_length
                        point.elevation = self.get_elevation(point.latitude, point.longitude)
                    else:
                        point.elevation = None
                    previous_point = point
        gpx.add_missing_elevations()

    def _add_sampled_elevations(self, gpx: Any) -> None:
        # Use some random intervals here to randomize a bit:
        self._add_interval_elevations(gpx, min_interval_length=35)
        elevations_1 = list(map(lambda point: point.elevation, gpx.walk(only_points=True))) # type: ignore
        self._add_interval_elevations(gpx, min_interval_length=141)
        elevations_2 = list(map(lambda point: point.elevation, gpx.walk(only_points=True))) # type: ignore
        self._add_interval_elevations(gpx, min_interval_length=241)
        elevations_3 = list(map(lambda point: point.elevation, gpx.walk(only_points=True))) # type: ignore

        n = 0
        for point in gpx.walk(only_points=True):
            if elevations_1[n] != None and elevations_2[n] != None and elevations_3[n] != None:
                #print elevations_1[n], elevations_2[n], elevations_3[n]
                point.elevation = (elevations_1[n] + elevations_2[n] + elevations_3[n]) / 3.
            else:
                point.elevation = None
            n += 1

class GeoElevationFile:
    """
    Contains data from a single Shuttle elevation file.

    This class hould not be instantiated without its GeoElevationData because
    it may need elevations from nearby files.
    """


    def __init__(self, file_name: str, data: bytes, geo_elevation_data: GeoElevationData) -> None:
        """ Data is a raw file contents of the file. """

        self.url: Optional[str] = None
        self.geo_elevation_data = geo_elevation_data
        self.file_name = file_name

        self.latitude: float = 0
        self.longitude: float = 0
        self.parse_file_name_starting_position()

        self.data = data

        square_side = mod_math.sqrt(len(self.data) / 2.)
        assert square_side == int(square_side), 'Invalid file size: {0} for file {1}'.format(len(self.data), self.file_name)

        self.resolution = 1.0 / (square_side - 1)
        self.square_side = int(square_side)

    def get_row_and_column(self, latitude: float, longitude: float) -> Tuple[int, int]:
        return mod_math.floor((self.latitude + 1 - latitude) * float(self.square_side - 1)), \
               mod_math.floor((longitude - self.longitude) * float(self.square_side - 1))

    def get_lat_and_long(self, row: int, column: int) -> Tuple[float, float]:
        return self.latitude + 1 - row *  self.resolution, \
               self.longitude + column * self.resolution

    def get_elevation(self, latitude: float, longitude: float, approximate: bool=False) -> Optional[float]:
        """
        If approximate is True then only the points from SRTM grid will be
        used, otherwise a basic aproximation of nearby points will be calculated.
        """
        if not (self.latitude - self.resolution <= latitude < self.latitude + 1):
            raise Exception('Invalid latitude %s for file %s' % (latitude, self.file_name))
        if not (self.longitude <= longitude < self.longitude + 1 + self.resolution):
            raise Exception('Invalid longitude %s for file %s' % (longitude, self.file_name))

        row, column = self.get_row_and_column(latitude, longitude)

        if approximate:
            return self.approximation(latitude, longitude)
        else:
            return self.get_elevation_from_row_and_column(int(row), int(column))

    def approximation(self, latitude: float, longitude: float) -> Optional[float]:
        """
        Dummy approximation with nearest points. The nearest the neighbour the
        more important will be its elevation.
        """
        d = 1. / self.square_side
        d_meters = d * mod_utils.ONE_DEGREE

        # Since the less the distance => the more important should be the
        # distance of the point, we'll use d-distance as importance coef
        # here:
        importance_1 = d_meters - mod_utils.distance(latitude + d, longitude, latitude, longitude)
        elevation_1  = self.geo_elevation_data.get_elevation(latitude + d, longitude, approximate=False)

        importance_2 = d_meters - mod_utils.distance(latitude - d, longitude, latitude, longitude)
        elevation_2  = self.geo_elevation_data.get_elevation(latitude - d, longitude, approximate=False)

        importance_3 = d_meters - mod_utils.distance(latitude, longitude + d, latitude, longitude)
        elevation_3  = self.geo_elevation_data.get_elevation(latitude, longitude + d, approximate=False)

        importance_4 = d_meters - mod_utils.distance(latitude, longitude - d, latitude, longitude)
        elevation_4  = self.geo_elevation_data.get_elevation(latitude, longitude - d, approximate=False)
        # TODO(TK) Check if coordinates inside the same file, and only then decide if to call
        # self.geo_elevation_data.get_elevation or just self.get_elevation

        if elevation_1 == None or elevation_2 == None or elevation_3 == None or elevation_4 == None:
            elevation = self.get_elevation(latitude, longitude, approximate=False)
            if not elevation:
                return None
            elevation_1 = elevation_1 or elevation
            elevation_2 = elevation_2 or elevation
            elevation_3 = elevation_3 or elevation
            elevation_4 = elevation_4 or elevation

        # Normalize importance:
        sum_importances = float(importance_1 + importance_2 + importance_3 + importance_4)

        # Check normalization:
        assert abs(importance_1 / sum_importances + \
                   importance_2 / sum_importances + \
                   importance_3 / sum_importances + \
                   importance_4 / sum_importances - 1 ) < 0.000001

        if elevation_1 is not None and elevation_2 is not None and elevation_3 is not None and elevation_4 is not None:
            return importance_1 / sum_importances * elevation_1 + \
                importance_2 / sum_importances * elevation_2 + \
                importance_3 / sum_importances * elevation_3 + \
                importance_4 / sum_importances * elevation_4

        return None

    def _InverseDistanceWeighted(self, latitude: float, longitude: float, radius: float=1) -> Optional[float]:
        """
        Return the Inverse Distance Weighted Elevation.

        Interpolate the elevation of the given point using the inverse
        distance weigthing algorithm (exp of 1) in the form:
            sum((1/distance) * elevation)/sum(1/distance)
            for each point in the matrix.
        The matrix size is determined by the radius. A radius of 1 uses
        5 points and a radius of 2 uses 13 points. The matrices are set
        up to use cells adjacent to and including the one that contains
        the given point. Any cells referenced by the matrix that are on
        neighboring tiles are ignored.

        Args:
            latitude: float of the latitude in decimal degrees
            longitude: float of the longitude in decimal degrees
            radius: int of 1 or 2 indicating the size of the matrix

        Returns:
            a float of the interpolated elevation in the same units as
            the underlying .hgt file (meters)

        Exceptions:
            raises a ValueError if an invalid radius is supplied

        """
        if radius == 1:
            offsetmatrix: Any = (None, (0, 1), None,
                           (-1, 0), (0, 0), (1, 0),
                           None, (0, -1), None)
        elif radius == 2:
            offsetmatrix = (None, None, (0, 2), None, None,
                            None, (-1, 1), (0, 1), (1, 1), None,
                            (-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0),
                            None, (-1, -1), (0, -1), (1, -1), None,
                            None, None, (0, -2), None, None)
        else:
            raise ValueError("Radius {} invalid, "
                             "expected 1 or 2".format(radius))

        row, column = self.get_row_and_column(latitude, longitude)
        center_lat, center_long = self.get_lat_and_long(row, column)
        if latitude == center_lat and longitude == center_long:
            # return direct elev at point (infinite weight)
            return self.get_elevation_from_row_and_column(int(row), int(column))
        weights: float = 0
        elevation: float = 0

        for offset in offsetmatrix:
            if (offset is not None and
                0 <= row + offset[0] < self.square_side and
                0 <= column + offset[1] < self.square_side):
                cell = self.get_elevation_from_row_and_column(int(row + offset[0]),
                                                              int(column + offset[1]))
                if cell is not None:
                    # does not need to be meters, anything proportional
                    distance = mod_utils.distance(latitude, longitude,
                                                  center_lat + float(offset[0])/(self.square_side-1),
                                                  center_long + float(offset[1])/(self.square_side-1))
                    weights += 1/distance
                    elevation += cell/distance
        return elevation/weights

    def get_elevation_from_row_and_column(self, row: int, column: int) -> Optional[float]:
        i = row * (self.square_side) + column
        assert i < len(self.data) - 1

        #mod_logging.debug('{0}, {1} -> {2}'.format(row, column, i))

        unpacked = mod_struct.unpack(">h", self.data[i * 2 : i * 2 + 2])
        result: Optional[float] = None
        if unpacked and len(unpacked) == 1:
            result = unpacked[0]

        if (result is None) or result > 10000 or result < -1000:
            return None

        return result

    def parse_file_name_starting_position(self) -> None:
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

    def __str__(self) -> str:
        return f'[{self.__class__}:{self.file_name}]'
