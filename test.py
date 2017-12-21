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
Run all tests with:
    $ python -m unittest test
"""

import logging as mod_logging
import unittest as mod_unittest
import hashlib as mod_hashlib
import os as mod_os
import getpass as mod_getpass

import srtm as mod_srtm
from srtm import data as mod_data
from srtm import main as mod_main

mod_logging.basicConfig(level=mod_logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

def localfetchv2_3a(url):
    """
    Read the data of a local v2.3a test file

    Reads the data from a local file instead of fetching from the
    network. To use, store the function to the callable of the GeoElevationData
    instance. Prints to stdout that a local fetch happens.
    
    Example:
            tilemap = mod_data.GeoElevationData(file_handler=mod_main.FileHandler())
            tilemap.fetch = localfetchv2_3a
            tilemap.get_elevation(latitude, longitude)

    Args:
        url: str of the url to download

    Returns:
        data from the local test file with the same name specified in url
    """
    remotefile = url.split('/')[-1]
    localname = '{}v2.3a.hgt.zip'.format(remotefile.partition('.')[0])
    print("Local fetch: loading ./test_files/{} instead of {}".format(localname, url))
    with open("test_files/" + localname, "rb") as hgtfile:
        return hgtfile.read()

class Tests(mod_unittest.TestCase):

    def test_dead_sea(self):
        geo_elevation_data = mod_srtm.get_data()
        self.assertEqual(-415, geo_elevation_data.get_elevation(31.5, 35.5))

    def test_random_points(self):
        geo_elevation_data = mod_srtm.get_data()
        self.assertEqual(63, geo_elevation_data.get_elevation(46., 13.))
        self.assertEqual(2714, geo_elevation_data.get_elevation(46.999999, 13.))
        self.assertEqual(1643, geo_elevation_data.get_elevation(46.999999, 13.999999))
        self.assertEqual(553, geo_elevation_data.get_elevation(46., 13.999999))
        self.assertEqual(203, geo_elevation_data.get_elevation(45.2732, 13.7139))
        self.assertEqual(460, geo_elevation_data.get_elevation(45.287, 13.905))

    def test_around_zero_longitude(self):
        geo_elevation_data = mod_srtm.get_data()
        self.assertEqual(61, geo_elevation_data.get_elevation(51.2, 0.0))
        self.assertEqual(100, geo_elevation_data.get_elevation(51.2, -0.1))
        self.assertEqual(59, geo_elevation_data.get_elevation(51.2, 0.1))

    def test_around_zero_latitude(self):
        geo_elevation_data = mod_srtm.get_data()
        self.assertEqual(393, geo_elevation_data.get_elevation(0, 15))
        self.assertEqual(423, geo_elevation_data.get_elevation(-0.1, 15))
        self.assertEqual(381, geo_elevation_data.get_elevation(0.1, 15))

    def test_point_with_invalid_elevation(self):
        geo_elevation_data = mod_srtm.get_data()
        self.assertEqual(None, geo_elevation_data.get_elevation(47.0, 13.07))

    def test_point_without_file(self):
        geo_elevation_data = mod_srtm.get_data()
        print(geo_elevation_data.get_elevation(0, 0))

    def test_files_equality(self):
        geo_elevation_data = mod_srtm.get_data()
        self.assertEqual(geo_elevation_data.get_file(47.0, 13.99),
                          geo_elevation_data.get_file(47.0, 13.0))
        self.assertEqual(geo_elevation_data.get_file(47.99, 13.99),
                          geo_elevation_data.get_file(47.0, 13.0))

        self.assertEqual(geo_elevation_data.get_file(-47.0, 13.99),
                          geo_elevation_data.get_file(-47.0, 13.0))
        self.assertEqual(geo_elevation_data.get_file(-47.99, 13.99),
                          geo_elevation_data.get_file(-47.0, 13.0))

        self.assertEqual(geo_elevation_data.get_file(-47.0, -13.99),
                          geo_elevation_data.get_file(-47.0, -13.0))
        self.assertEqual(geo_elevation_data.get_file(-47.99, -13.99),
                          geo_elevation_data.get_file(-47.0, -13.0))

        self.assertEqual(geo_elevation_data.get_file(47.0, -13.99),
                          geo_elevation_data.get_file(47.0, -13.0))
        self.assertEqual(geo_elevation_data.get_file(47.99, -13.99),
                          geo_elevation_data.get_file(47.0, -13.0))

    def test_invalit_coordinates_for_file(self):
        geo_elevation_data = mod_srtm.get_data()
        geo_file = geo_elevation_data.get_file(47.0, 13.99)

        try:
            self.assertFalse(geo_file.get_elevation(1, 1))
        except Exception as e:
            message = str(e)
            self.assertEqual('Invalid latitude 1 for file N47E013.hgt', message)

        try:
            self.assertFalse(geo_file.get_elevation(47, 1))
        except Exception as e:
            message = str(e)
            self.assertEqual('Invalid longitude 1 for file N47E013.hgt', message)

    def test_invalid_file(self):
        geo_elevation_data = mod_srtm.get_data()
        geo_file = geo_elevation_data.get_file(-47.0, -13.99)
        self.assertEqual(None, geo_file)

    def test_coordinates_in_file(self):
        geo_elevation_data = mod_srtm.get_data()
        geo_file = geo_elevation_data.get_file(47.0, 13.99)

        print('file:', geo_file)

        self.assertEqual(geo_file.get_elevation(47, 13),
                          geo_file.get_elevation(47, 13))

    def test_coordinates_row_col_conversion(self):
        geo_elevation_data = mod_srtm.get_data()
        geo_file = geo_elevation_data.get_file(47.0, 13.99)

        print('file:', geo_file)

        r, c = geo_file.get_row_and_column(47, 13)
        lat, long = geo_file.get_lat_and_long(r, c)
        self.assertEqual(lat, 47)
        self.assertEqual(long, 13)

        r, c = geo_file.get_row_and_column(46.5371, 8.1264)
        lat, long = geo_file.get_lat_and_long(r, c)
        self.assertAlmostEqual(lat, 46.5371, delta=geo_file.resolution)
        self.assertAlmostEqual(long, 8.1264, delta=geo_file.resolution)

    def test_without_approximation(self):
        geo_elevation_data = mod_srtm.get_data()

        self.assertEqual(geo_elevation_data.get_elevation(47.1, 13.1, approximate=False),
                          geo_elevation_data.get_elevation(47.1, 13.1))

        # SRTM elevations are always integers:
        elevation = geo_elevation_data.get_elevation(47.1, 13.1)
        self.assertTrue(int(elevation) == elevation)

    def test_with_approximation(self):
        geo_elevation_data = mod_srtm.get_data()

        self.assertNotEquals(geo_elevation_data.get_elevation(47.1, 13.1, approximate=True),
                             geo_elevation_data.get_elevation(47.1, 13.1))

        # When approximating a random point, it probably won't be a integer:
        elevation = geo_elevation_data.get_elevation(47.1, 13.1, approximate=True)
        self.assertTrue(int(elevation) != elevation)

    def test_approximation(self):
        # TODO(TK) Better tests for approximation here:
        geo_elevation_data = mod_srtm.get_data()
        elevation_without_approximation = geo_elevation_data.get_elevation(47, 13)
        elevation_with_approximation = geo_elevation_data.get_elevation(47, 13, approximate=True)

        print(elevation_without_approximation)
        print(elevation_with_approximation)

        self.assertNotEquals(elevation_with_approximation, elevation_without_approximation)
        self.assertTrue(abs(elevation_with_approximation - elevation_without_approximation) < 30)

    def test_batch_mode(self):
        
        # Two pulls that are far enough apart to require multiple files
        lat1, lon1 = 22.5, -159.5
        lat2, lon2 = 19.5, -154.5
        tilemap = mod_data.GeoElevationData(file_handler=mod_main.FileHandler(), batch_mode=False)
        tilemap.fetch = localfetchv2_3a # Use local test files only
        tilemap.tiles = {} # Flush cache from other tests
        
        # With batch_mode=False, both files should be kept
        tilemap.get_elevation(lat1, lon1)
        self.assertEqual(len(tilemap.tiles), 1)

        tilemap.get_elevation(lat2, lon2)
        self.assertEqual(len(tilemap.tiles), 2)

        # With batch_mode=True, only the most recent file should be kept
        tilemap = mod_data.GeoElevationData(file_handler=mod_main.FileHandler(), batch_mode=True)
        tilemap.fetch = localfetchv2_3a # Use local test files only
        tilemap.get_elevation(lat1, lon1)
        self.assertEqual(len(tilemap.tiles), 1)
        keys1 = tilemap.tiles.keys()

        tilemap.get_elevation(lat2, lon2)
        self.assertEqual(len(tilemap.tiles), 1)
        self.assertNotEqual(tilemap.tiles.keys(), keys1)

    def test_build_url(self):
        print("Testing: _build_url")
        tilemap = mod_data.GeoElevationData(file_handler=mod_main.FileHandler())
        tilename = 'N44W072'
        self.assertEqual(tilemap._build_url(tilename, 'v3.1a'),'https://e4ftl01.cr.usgs.gov/MODV6_Dal_D/SRTM/SRTMGL1.003/2000.02.11/N44W072.SRTMGL1.hgt.zip')
        self.assertEqual(tilemap._build_url(tilename, 'v3.3a'),'https://e4ftl01.cr.usgs.gov/MODV6_Dal_D/SRTM/SRTMGL3.003/2000.02.11/N44W072.SRTMGL3.hgt.zip')
        self.assertEqual(tilemap._build_url(tilename, 'v3.3as'),'https://e4ftl01.cr.usgs.gov/MODV6_Dal_D/SRTM/SRTMGL3S.003/2000.02.11/N44W072.SRTMGL3.hgt.zip')
        self.assertEqual(tilemap._build_url(tilename, 'v2.1a'),'https://dds.cr.usgs.gov/srtm/version2_1/SRTM1/Region_06/N44W072.hgt.zip')
        self.assertEqual(tilemap._build_url(tilename, 'v2.3a'),'https://dds.cr.usgs.gov/srtm/version2_1/SRTM3/North_America/N44W072.hgt.zip')
        #self.assertEqual(tilemap._build_url(tilename, 'v2.3as'),'') No data source implemented
        self.assertEqual(tilemap._build_url(tilename, 'v1.1a'),'https://dds.cr.usgs.gov/srtm/version1/United_States_1arcsec/1arcsec/N44W072.hgt.zip')
        self.assertEqual(tilemap._build_url(tilename, 'v1.3a'),'https://dds.cr.usgs.gov/srtm/version1/North_America_3arcsec/3arcsec/N44W072.hgt.zip')

    def test_fetch(self):
        # TODO: Download from ED server with bad credentials
        # TODO: Download bad url
        # super tiny tile is N22W160, should be present in all versions
        print("Testing: fetch")
        user = 'ptolemytemp' # mod_os.environ.get('SRTMEDUser')
        password = 'Srtmpass1' # mod_os.environ.get('SRTMEDPass')
        if not user or not password:
            user = input('Username: ')
            password = mod_getpass.getpass()
        #Download from EarthData (ED) server with credentials
        tilemap = mod_data.GeoElevationData(file_handler=mod_main.FileHandler(), EDuser=user, EDpass=password)
        url = "https://e4ftl01.cr.usgs.gov/MODV6_Dal_D/SRTM/SRTMGL3.003/2000.02.11/N22W160.SRTMGL3.hgt.zip"
        self.assertEqual(mod_hashlib.sha1(tilemap.fetch(url)).hexdigest(),'271c36d4295238d84a82682dd7fd1e59120cb83b')
        
        # Download from non-ED server with credentials
        url = 'https://dds.cr.usgs.gov/srtm/version1/Islands/N22W160.hgt.zip'
        self.assertEqual(mod_hashlib.sha1(tilemap.fetch(url)).hexdigest(),'3f0e957caa5c300562fe8328ce54433639e4910e')

        # Download from non-ED server with bad credentials
        tilemap.EDpass=''
        url = 'https://dds.cr.usgs.gov/srtm/version1/Islands/N22W160.hgt.zip'
        self.assertEqual(mod_hashlib.sha1(tilemap.fetch(url)).hexdigest(),'3f0e957caa5c300562fe8328ce54433639e4910e')

    def test_load_tile(self):

        # Setup
        print("Testing: load_tile")
        tilename = 'N22W160'
        version = 'v2.3a'
        tilemap = mod_data.GeoElevationData(file_handler=mod_main.FileHandler())
        tilemap.fetch = localfetchv2_3a # Use local test files only
        srtmdir = tilemap.file_handler.get_srtm_dir()
        # Clean cache
        if tilemap.file_handler.exists(tilename+version+'.hgt'):
            mod_os.remove(srtmdir+mod_os.sep+tilename+version+'.hgt')
        if tilemap.file_handler.exists(tilename+version+'.hgt.zip'):
            mod_os.remove(srtmdir+mod_os.sep+tilename+version+'.hgt.zip')
        self.assertFalse(tilemap.file_handler.exists(tilename+version+'.hgt'))
        self.assertFalse(tilemap.file_handler.exists(tilename+version+'.hgt.zip'))

        # Download unzipped
        self.assertFalse('N22W160v2.3a' in tilemap.tiles)
        tile = tilemap.load_tile(tilename, version)
        self.assertEqual(tile.latitude, 22)
        self.assertEqual(tile.longitude, -160)
        self.assertEqual(mod_hashlib.sha1(tile.data).hexdigest(),'29862497be67be942b323a65a2e400b941ff4a85')
        self.assertTrue(tile is tilemap.tiles['N22W160v2.3a'])
        self.assertTrue(tilemap.file_handler.exists('N22W160v2.3a.hgt'))
        # Cleanup
        mod_os.replace(srtmdir+mod_os.sep+'N22W160v2.3a.hgt', srtmdir+mod_os.sep+'N99W160v2.3a.hgt')
        self.assertFalse(tilemap.file_handler.exists('N22W160v2.3a.hgt'))

        # Download zipped
        tilemap.leave_zipped = True
        tilemap.tiles = {}
        tile = tilemap.load_tile(tilename, version)
        self.assertEqual(tile.latitude, 22)
        self.assertEqual(tile.longitude, -160)
        self.assertEqual(mod_hashlib.sha1(tile.data).hexdigest(),'29862497be67be942b323a65a2e400b941ff4a85')
        self.assertTrue(tile is tilemap.tiles['N22W160v2.3a'])
        self.assertTrue(tilemap.file_handler.exists('N22W160v2.3a.hgt.zip'))
        # Cleanup
        mod_os.replace(srtmdir+mod_os.sep+'N22W160v2.3a.hgt.zip', srtmdir+mod_os.sep+'N98W160v2.3a.hgt.zip')
        self.assertFalse(tilemap.file_handler.exists('N22W160v2.3a.hgt.zip'))

        # Load unzipped from cache
        self.assertFalse('N99W160v2.3a' in tilemap.tiles)
        tile = tilemap.load_tile('N99W160', version) #Invalid tile, only in cache
        self.assertEqual(tile.latitude, 99)
        self.assertEqual(tile.longitude, -160)
        self.assertEqual(mod_hashlib.sha1(tile.data).hexdigest(),'29862497be67be942b323a65a2e400b941ff4a85')
        self.assertTrue(tile is tilemap.tiles['N99W160v2.3a'])
        # Cleanup
        del tilemap.tiles['N99W160v2.3a']
        mod_os.remove(srtmdir+mod_os.sep+'N99W160v2.3a.hgt')

        # Load zipped from cache
        self.assertFalse('N98W160v2.3a' in tilemap.tiles)
        tile = tilemap.load_tile('N98W160', version) #Invalid tile, only in cache
        self.assertEqual(tile.latitude, 98)
        self.assertEqual(tile.longitude, -160)
        self.assertEqual(mod_hashlib.sha1(tile.data).hexdigest(),'29862497be67be942b323a65a2e400b941ff4a85')
        self.assertTrue(tile is tilemap.tiles['N98W160v2.3a'])
        # Cleanup
        del tilemap.tiles['N98W160v2.3a']
        mod_os.remove(srtmdir+mod_os.sep+'N98W160v2.3a.hgt.zip')
        
        # Check invalid tile
        self.assertTrue(tilemap.load_tile('N99W999', version) is None) 

    def test_get_tilename(self):
        print("Testing: get_filename")
        tilemap = mod_data.GeoElevationData(file_handler=mod_main.FileHandler())
        # Each quadrant
        self.assertEqual("N01E001", tilemap.get_tilename(1.5, 1.5))
        self.assertEqual("N01W002", tilemap.get_tilename(1.5, -1.5))
        self.assertEqual("S02E001", tilemap.get_tilename(-1.5, 1.5))
        self.assertEqual("S02W002", tilemap.get_tilename(-1.5, -1.5))
        # Equator and Prime Meridian
        self.assertEqual("N00E001", tilemap.get_tilename(0, 1.5))
        self.assertEqual("N01E000", tilemap.get_tilename(1.5, 0))
        self.assertEqual("N00E000", tilemap.get_tilename(0, 0))       

    def test_fallback(self):
        print("Testing: fallback")
        tilemap = mod_data.GeoElevationData(file_handler=mod_main.FileHandler())
        self.assertEqual(tilemap.fallback_version('v3.1a'),'v3.3a')
        self.assertEqual(tilemap.fallback_version('v3.3a'),'v2.3a')
        self.assertEqual(tilemap.fallback_version('v3.3as'),'v3.3a')
        self.assertEqual(tilemap.fallback_version('v2.1a'),'v2.3a')
        self.assertTrue(tilemap.fallback_version('v2.3a') is None)
        self.assertEqual(tilemap.fallback_version('v2.3as'),'v2.3a')
        self.assertEqual(tilemap.fallback_version('v1.1a'),'v1.3a')
        self.assertTrue(tilemap.fallback_version('v1.3a') is None)
        self.assertTrue(tilemap.fallback_version('blah') is None)
        self.assertTrue(tilemap.fallback_version(None) is None)
        

    def test_get_elevation(self):
        # test basic point
        # loads tile from memory
        # loads from disk
        # test fallback behavior T/F
        pass

if __name__ == '__main__':
    mod_unittest.main()
