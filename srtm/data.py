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
import warnings as mod_warnings
import json as mod_json
import os as mod_os
import os.path as mod_path

from . import utils as mod_utils

import requests as mod_requests

# TODO Update this section to load data from pkg_resources
package_location = __file__[:__file__.rfind(mod_path.sep)]
SRTM_JSON = package_location + mod_path.sep + 'srtm.json'
DEFAULT_LIST_JSON = package_location + mod_os.sep + 'list.json'


class GeoElevationData:
    """
    The main class with utility methods for elevations.

    Note that files are loaded in memory, so if you need to find
    elevations for multiple points on the earth -- this will load
    *many* files in memory!

    Methods:
        __init__: initialize new instance
        _build_url: return url for requested tile
        get_elevation: return elevation at a point
        fallback_version:
        get_file: (Deprecated) load and return GeoElevationFile
        retrieve_or_load_file_data: (Deprecated) load or download data
            and return it
        _fetch: download and return the requested url
        _load_tile: load or download requested tile and return the
            GeoElevationFile
        get_file_name: (Deprecated) Build base of file name and check
            if it is valid
        _get_tilename: return the base of the tile name
        get_image: ?
        add_elevations: ?
        _add_interval_elevations: ?
        _add_sampled_elevations ?

    Attributes:
        srtm1_files: (Deprecated) dict of v2.1a tiles, may not be valid
        srtm3_files: (Deprecated) dict of v2.3a tiles, may not be valid
        tile_index: dict of lists that hold lookup information for each
            data set. Keys are of form. 'N00E000'. The lists are of
            form: [bool, str, str, str, bool]. First and last bools are
            whether the tiles are valid v1.1a and v3.*, respectively.
            The first str is v1.3a continent code, second str is v2.1a
            region code (US only), third str is v2.3a(s) continent code.
            Empty str indicate it is not a valid tile.
        tiles: dict of GeoElevationFile that is currently loaded in
            memory for fast access. Keys are of form: 'N00E000v2.1a'

    """

    # Deprecated attributes
    srtm1_files = None
    srtm3_files = None

    # Share memory with other instances
    tile_index = {}
    tiles = {}

    def __init__(self, srtm1_files=None, srtm3_files=None, version='v2.1a',
                 fallback=True, leave_zipped=False, file_handler=None,
                 batch_mode=False, EDuser='', EDpass=''):
        """
        Initialize a new instance of GeoElevationData.

        If tile_index is empty, load it from srtm.json. If no
        file_handler is provided, create a new default FileHandler.

        Args:
            srtm1_files: (Deprecated) If supplied, assume user wanted
                v2.1a data as set that as the version
            srtm3_files: (Deprecated) If supplied and srtm1_files was
                not, assume the user wanted v2.3a data and set version
            version: str of version to load by default. Options are-
                v1.1a, v1.3a, v2.1a, v2.3a, v2.3as, v3.1a, v3.3a, v3.3as
                vX indicates the SRTM version and Ya(s) indicates the
                sampling. 1 for 1 arcsecond, 3 for 3 arcsecond. Using s
                will choose between 3x3 average vs center sampled. Read
                NASA's SRTM documentation for more information on
                versions and sampling
            fallback: bool, when true, fallback on failures
            leave_zipped: bool, chooses to store tiles compressed or not
            file_handler: FileHandler used for reading and writing to
                disk cache
            batch_mode: bool, when true, keeps at most 1 tile in memory
            EDuser: str of EarthData username
            EDpass: str of EarthData password

        """
        # Deprecated parameter handling
        if srtm1_files is not None or srtm3_files is not None:
            mod_warnings.warn("Use of srtm1_files and srtm3_files is "
                              "deprecated. Use version instead",
                              DeprecationWarning)
        if srtm1_files is not None:
            version = 'v2.1a'
        elif srtm3_files is not None:
            version = 'v2.3a'
        # End deprecated parameter handling

        if not GeoElevationData.tile_index:
            # v1-1, v1-3, v2-1, v2-3, v3
            # bool, str, str, str, bool
            with open(SRTM_JSON, 'r') as indexfile:
                GeoElevationData.tile_index = mod_json.load(indexfile)

        self.version = version
        self.leave_zipped = leave_zipped
        self.file_handler = file_handler if file_handler else FileHandler()
        self.batch_mode = batch_mode
        self.fallback = fallback
        self.EDuser = EDuser
        self.EDpass = EDpass

        # Deprecated init
        self.srtm1_files = srtm1_files
        self.srtm3_files = srtm3_files
        self.files = {}
        # End deprecated init

    def _build_url(self, tilename, version):
        """
        Return the URL to for the given tilename and version.

        Use the tile_index to build up the correct URL for each version
        and tilename.

        Args:
            tilename: str of the tile (form "N00E000")
            version: str of the SRTM data version and resolution to get.
                Values can be v1.1a, v1.3a, v2.1a, v2.3a, v3.1a, v3.3a,
                v3.3as

        Returns:
            The URL to the file or None if the tile does not exist

        """
        if tilename not in GeoElevationData.tile_index:
            return None
        if version == 'v3.1a':
            if GeoElevationData.tile_index[tilename][4]:
                return 'https://e4ftl01.cr.usgs.gov/MODV6_Dal_D/SRTM/SRTMGL1.003/2000.02.11/{}.SRTMGL1.hgt.zip'.format(tilename)
        elif version == 'v3.3a':
            if GeoElevationData.tile_index[tilename][4]:
                return 'https://e4ftl01.cr.usgs.gov/MODV6_Dal_D/SRTM/SRTMGL3.003/2000.02.11/{}.SRTMGL3.hgt.zip'.format(tilename)
        elif version == 'v3.3as':
            if GeoElevationData.tile_index[tilename][4]:
                return 'https://e4ftl01.cr.usgs.gov/MODV6_Dal_D/SRTM/SRTMGL3S.003/2000.02.11/{}.SRTMGL3S.hgt.zip'.format(tilename)
        elif version == 'v2.1a':
            if GeoElevationData.tile_index[tilename][2]:
                return 'https://dds.cr.usgs.gov/srtm/version2_1/SRTM1/Region_{}/{}.hgt.zip'.format(GeoElevationData.tile_index[tilename][2], tilename)
        elif version == 'v2.3a':
            if GeoElevationData.tile_index[tilename][3]:
                return 'https://dds.cr.usgs.gov/srtm/version2_1/SRTM3/{}/{}.hgt.zip'.format(GeoElevationData.tile_index[tilename][3], tilename)
        elif version == 'v2.3as':
            return None  # Find a data source...
        elif version == 'v1.1a':
            if GeoElevationData.tile_index[tilename][0]:
                return 'https://dds.cr.usgs.gov/srtm/version1/United_States_1arcsec/1arcsec/{}.hgt.zip'.format(tilename)
        elif version == 'v1.3a':
            if GeoElevationData.tile_index[tilename][1]:
                return 'https://dds.cr.usgs.gov/srtm/version1/{}/{}.hgt.zip'.format(GeoElevationData.tile_index[tilename][1], tilename)
        else:
            return None

    def get_elevation(self, latitude, longitude, approximate=None,
                      version=None):
        """
        Return the elevation at the point specified.

        Args:
            latitude: float of the latitude in decimal degrees
            longitude: float of the longitude in decimal degrees
            approximate: bool passed to GeoElevationFile.get_elevation
            version: str of the SRTM data version and resolution to get.
                Values are determined by _build_url()

        Returns:
            A float passed back from GeoElevationFile.get_elevation().
            Value should be the elevation of the point in meters.

        """
        if version is None:
            version = self.version
        tilename = self._get_tilename(latitude, longitude)
        if tilename + version in self.tiles:
            geo_elevation_file = self.tiles[tilename + version]
        else:
            geo_elevation_file = self._load_tile(tilename, version)

        if not geo_elevation_file:
            if self.fallback and self.fallback_version(version) is not None:
                return self.get_elevation(latitude, longitude, approximate,
                                          self.fallback_version(version))
            else:
                return None

        return geo_elevation_file.get_elevation(latitude, longitude,
                                                approximate)

    def fallback_version(self, version):
        """
        Return the next version in the fallback order.

        The order is defined as:
        v3.1a -> v3.3a -> v2.3a -> None
        v3.3as -> v3.3a
        v2.1a -> v2.3a
        v2.3as -> v2.3a
        v1.1a -> v1.3a -> None

        To change the fallback order you can subclass or save a function
        back to the instance. The function must take one argument and
        eventually must return None to prevent infinite recursion.
        Example in user code:

        def my_order(oldversion):
            return None

        myGeoData = GeoElevationData()
        myGeoData.fallback_version = my_order
        myGeoData.get_elevation(mylatitude, mylongitude)

        Args:
            version: str of the current version

        Returns:
            str of the next version to try

        """
        if version == 'v3.1a':
            return 'v3.3a'
        elif version == 'v3.3a':
            return 'v2.3a'
        elif version == 'v3.3as':
            return 'v3.3a'
        elif version == 'v2.1a':
            return 'v2.3a'
        elif version == 'v2.3a':
            return None
        elif version == 'v2.3as':
            return 'v2.3a'
        elif version == 'v1.1a':
            return 'v1.3a'
        elif version == 'v1.3a':
            return None
        return None

    def get_file(self, latitude, longitude):
        """
        Deprecated.

        If the file can't be found -- it will be retrieved from the server.
        """
        mod_warnings.warn("Use of get_file is deprecated. Use load_tile "
                          "and get_tilename instead", DeprecationWarning)

        tilename = self._get_tilename(latitude, longitude)
        version = self.version

        tile = None
        while tile is None and version is not None:
            if tilename + version in self.tiles:
                return self.tiles[tilename + version]
            tile = self._load_tile(tilename, version)
            version = self.fallback_version(version)
        return tile

    def retrieve_or_load_file_data(self, file_name):
        """Deprecated."""
        mod_warnings.warn("Use of retrieve_or_load_file_data is deprecated. Use load_tile instead", DeprecationWarning)
        
        data_file_name = file_name
        zip_data_file_name = '{0}.zip'.format(file_name)

        if self.file_handler.exists(data_file_name):
            return self.file_handler.read(data_file_name)
        elif self.file_handler.exists(zip_data_file_name):
            data = self.file_handler.read(zip_data_file_name)
            return mod_utils.unzip(data)

        url = None

        if (file_name in self.srtm1_files):
            url = self.srtm1_files[file_name]
        elif (file_name in self.srtm3_files):
            url = self.srtm3_files[file_name]

        if not url:
            #mod_logging.error('No file found: {0}'.format(file_name))
            return None

        try:
            r = mod_requests.get(url, timeout=5)
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

    def _fetch(self, url):
        """
        Download the file.

        Download the given URL using the credentials stored in EDuser
        and EDpass

        Args:
            url: str of the URL to download

        Returns:
            Data contained in the file at the requested URL.

        """
        with EarthDataSession(self.EDuser, self.EDpass) as s:
            response = s.get(url, timeout=5)
            response.raise_for_status()
            data = response.content
        return data

    def _load_tile(self, tilename, version):
        """
        Load the requested tile from cache or the network.

        Check to see if the tile needed is stored in local cache.
        If it isn't, download the tile from the network and save it
        in the local cache in compressed or uncompressed form based on
        self.leave_zipped. Load the tile into memory as a
        GeoElevationFile in the GeoElevationData.tiles dictionary.
        Return the tile.

        Args:
            tilename: str of the tile (form "N00E000")
            version: str of the SRTM data version and resolution to get.
                Values are determined by _build_url()

        Returns:
            GeoElevationFile containing the requested tile and version.

        """
        # Check local cache first
        data = None
        if self.file_handler.exists(tilename + version + '.hgt'):
            data = self.file_handler.read(tilename + version + '.hgt')
        elif self.file_handler.exists(tilename + version + '.hgt.zip'):
            data = self.file_handler.read(tilename + version + '.hgt.zip')
            data = mod_utils.unzip(data)

        # Download and save tile if needed
        if data is None:
            url = self._build_url(tilename, version)
            if url is not None:
                data = self._fetch(url)
                if self.leave_zipped:
                    self.file_handler.write(tilename + version
                                            + '.hgt.zip', data)
                data = mod_utils.unzip(data)
                if not self.leave_zipped:
                    self.file_handler.write(tilename + version + '.hgt', data)

        # Create GeoElevationFile
        if data is not None:
            tile = GeoElevationFile(tilename+'.hgt', data, self)
            if self.batch_mode:
                self.tiles = {tilename + version: tile}
            else:
                self.tiles[tilename + version] = tile
            return tile
        return None  # url is None or download failure

    def get_file_name(self, latitude, longitude):
        """Deprecated."""
        mod_warnings.warn("Use of get_file_name is deprecated. Use get_tilename instead", DeprecationWarning)
        file_name = self.get_tilename(latitude, longitude) + '.hgt'

        if not (file_name in self.srtm1_files) and not (file_name in self.srtm3_files):
            #mod_logging.debug('No file found for ({0}, {1}) (file_name: {2})'.format(latitude, longitude, file_name))
            return None

        return file_name

    def _get_tilename(self, latitude, longitude):
        """
        Return the tile name for the given coordinates.

        Tiles are 1 deg x 1 deg in size named after the bottom left
        corner cell. The corner cell is aligned on an interger value.
        Note that 0.x latitude is N and 0.x longitude is E.

        Args:
            latitude: float of the latitude in decimal degrees
            longitude: float of the longitude in decimal degrees

        Returns:
            str of the tilename (may not be a valid tile)
            
        """
        NS = "N" if latitude >= 0 else "S"
        EW = "E" if longitude >= 0 else "W"
        return (NS + str(int(abs(mod_math.floor(latitude)))).zfill(2) +
                EW + str(int(abs(mod_math.floor(longitude)))).zfill(3))

    def get_image(self, size, latitude_interval, longitude_interval, max_elevation, min_elevation=0,
                  unknown_color = (255, 255, 255, 255), zero_color = (0, 0, 255, 255),
                  min_color = (0, 0, 0, 255), max_color = (0, 255, 0, 255),
                  mode='image'):
        """
        Returns a numpy array or PIL image.
        """

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


        if mode == 'array':
            import numpy as np
            array = np.empty((height,width))
            for row in range(height):
                for column in range(width):
                    latitude  = latitude_from  + float(row) / height * (latitude_to  - latitude_from)
                    longitude = longitude_from + float(column) / height * (longitude_to - longitude_from)
                    elevation = self.get_elevation(latitude, longitude)
                    array[row,column] = elevation

            return array

        elif mode == 'image':
            try:    import Image as mod_image
            except: from PIL import Image as mod_image
            try:    import ImageDraw as mod_imagedraw
            except: from PIL import ImageDraw as mod_imagedraw

            image = mod_image.new('RGBA', (width, height),
                              (255, 255, 255, 255))
            draw = mod_imagedraw.Draw(image)

            max_elevation -= min_elevation

            for row in range(height):
                for column in range(width):
                    latitude  = latitude_from  + float(row) / height * (latitude_to  - latitude_from)
                    longitude = longitude_from + float(column) / height * (longitude_to - longitude_from)
                    elevation = self.get_elevation(latitude, longitude)
                    if elevation == None:
                        color = unknown_color
                    else:
                        elevation_coef = (elevation - min_elevation) / float(max_elevation)
                        if elevation_coef < 0: elevation_coef = 0
                        if elevation_coef > 1: elevation_coef = 1
                        color = mod_utils.get_color_between(min_color, max_color, elevation_coef)
                        if elevation <= 0:
                            color = zero_color
                    draw.point((column, height - row), color)

            return image
        else:
            raise Exception('Invalid mode ' + mode)

    def add_elevations(self, gpx, only_missing=False, smooth=False, gpx_smooth_no=0):
        """
        only_missing -- if True only points without elevation will get a SRTM value

        smooth -- if True interpolate between points

        if gpx_smooth_no > 0 -- execute gpx.smooth(vertical=True)
        """
        if only_missing:
            original_elevations = list(map(lambda point: point.elevation, gpx.walk(only_points=True)))

        if smooth:
            self._add_sampled_elevations(gpx)
        else:
            for point in gpx.walk(only_points=True):
                point.elevation = self.get_elevation(point.latitude, point.longitude)

        for i in range(gpx_smooth_no):
            gpx.smooth(vertical=True, horizontal=False)

        if only_missing:
            for original_elevation, point in zip(original_elevations, list(gpx.walk(only_points=True))):
                if original_elevation != None:
                    point.elevation = original_elevation

    def _add_interval_elevations(self, gpx, min_interval_length=100):
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

    def _add_sampled_elevations(self, gpx):
        # Use some random intervals here to randomize a bit:
        self._add_interval_elevations(gpx, min_interval_length=35)
        elevations_1 = list(map(lambda point: point.elevation, gpx.walk(only_points=True)))
        self._add_interval_elevations(gpx, min_interval_length=141)
        elevations_2 = list(map(lambda point: point.elevation, gpx.walk(only_points=True)))
        self._add_interval_elevations(gpx, min_interval_length=241)
        elevations_3 = list(map(lambda point: point.elevation, gpx.walk(only_points=True)))

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

    file_name = None
    url = None

    latitude = None
    longitude = None

    data = None

    def __init__(self, file_name, data, geo_elevation_data):
        """ Data is a raw file contents of the file. """

        self.geo_elevation_data = geo_elevation_data
        self.file_name = file_name

        self.parse_file_name_starting_position()

        self.data = data

        square_side = mod_math.sqrt(len(self.data) / 2.)
        assert square_side == int(square_side), 'Invalid file size: {0} for file {1}'.format(len(self.data), self.file_name)

        self.resolution = 1.0 / (square_side - 1)
        self.square_side = int(square_side)

    def get_row_and_column(self, latitude, longitude):
        return mod_math.floor((self.latitude + 1 - latitude) * float(self.square_side - 1)), \
               mod_math.floor((longitude - self.longitude) * float(self.square_side - 1))

    def get_lat_and_long(self, row, column):
        return self.latitude + 1 - row *  self.resolution, \
               self.longitude + column * self.resolution

    def get_elevation(self, latitude, longitude, approximate=None):
        """
        If approximate is True then only the points from SRTM grid will be
        used, otherwise a basic aproximation of nearby points will be calculated.
        """
        if not (self.latitude <= latitude < self.latitude + 1):
            raise Exception('Invalid latitude %s for file %s' % (latitude, self.file_name))
        if not (self.longitude <= longitude < self.longitude + 1):
            raise Exception('Invalid longitude %s for file %s' % (longitude, self.file_name))

        row, column = self.get_row_and_column(latitude, longitude)

        if approximate:
            return self.approximation(latitude, longitude)
        else:
            return self.get_elevation_from_row_and_column(int(row), int(column))

    def approximation(self, latitude, longitude):
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

        result = importance_1 / sum_importances * elevation_1 + \
               importance_2 / sum_importances * elevation_2 + \
               importance_3 / sum_importances * elevation_3 + \
               importance_4 / sum_importances * elevation_4

        return result

    def get_elevation_from_row_and_column(self, row, column):
        i = row * (self.square_side) + column
        assert i < len(self.data) - 1

        #mod_logging.debug('{0}, {1} -> {2}'.format(row, column, i))

        unpacked = mod_struct.unpack(">h", self.data[i * 2 : i * 2 + 2])
        result = None
        if unpacked and len(unpacked) == 1:
            result = unpacked[0]

        if (result is None) or result > 10000 or result < -1000:
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


class FileHandler:
    """
    The default file handler. It can be changed if you need to save/read SRTM
    files in a database or Amazon S3.
    """

    def get_srtm_dir(self):
        """ The default path to store files. """
        # Local cache path:
        result = ""
        if 'HOME' in mod_os.environ:
            result = mod_os.sep.join([mod_os.environ['HOME'], '.cache', 'srtm'])
        elif 'HOMEPATH' in mod_os.environ:
            result = mod_os.sep.join([mod_os.environ['HOMEPATH'], '.cache', 'srtm'])
        else:
            raise Exception('No default HOME directory found, please specify a path where to store files')

        if not mod_path.exists(result):
            mod_os.makedirs(result)

        return result

    def exists(self, file_name):
        return mod_path.exists('%s/%s' % (self.get_srtm_dir(), file_name))

    def write(self, file_name, contents):
        with open('%s/%s' % (self.get_srtm_dir(), file_name), 'wb') as f:
            f.write(contents)

    def read(self, file_name):
        with open('%s/%s' % (self.get_srtm_dir(), file_name), 'rb') as f:
            return f.read()


class EarthDataSession(mod_requests.Session):
    """
    Modify requests.Session to preserve Auth headers.

    Class comes from NASA docs on accessing their data servers.
    """
    AUTH_HOST = 'urs.earthdata.nasa.gov'

    def __init__(self, username, password):
        super(EarthDataSession, self).__init__()
        self.auth = (username, password)

    # Overrides from the library to keep headers when redirected to or from
    # the NASA auth host.
    def rebuild_auth(self, prepared_request, response):
        headers = prepared_request.headers
        url = prepared_request.url
        if 'Authorization' in headers:
            original_parsed = mod_requests.utils.urlparse(response.request.url)
            redirect_parsed = mod_requests.utils.urlparse(url)
            if (original_parsed.hostname != redirect_parsed.hostname) and \
                    redirect_parsed.hostname != self.AUTH_HOST and \
                    original_parsed.hostname != self.AUTH_HOST:
                del headers['Authorization']
        return
