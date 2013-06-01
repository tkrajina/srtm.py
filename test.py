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

import pdb

import logging        as mod_logging
import unittest as mod_unittest
import srtm           as mod_srtm

mod_logging.basicConfig(level=mod_logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

class Tests(mod_unittest.TestCase):

    def test_random_points(self):
        geo_elevation_data = mod_srtm.get_data()
        self.assertEquals(63, geo_elevation_data.get_elevation(46., 13.))
        self.assertEquals(2714, geo_elevation_data.get_elevation(46.999999, 13.))
        self.assertEquals(1643, geo_elevation_data.get_elevation(46.999999, 13.999999))
        self.assertEquals(553, geo_elevation_data.get_elevation(46., 13.999999))
        self.assertEquals(203, geo_elevation_data.get_elevation(45.2732, 13.7139))
        self.assertEquals(460, geo_elevation_data.get_elevation(45.287, 13.905))

    def test_around_zero_longitude(self):
        geo_elevation_data = mod_srtm.get_data()
        self.assertEquals(61, geo_elevation_data.get_elevation(51.2, 0.0))
        self.assertEquals(100, geo_elevation_data.get_elevation(51.2, -0.1))
        self.assertEquals(59, geo_elevation_data.get_elevation(51.2, 0.1))

    def test_around_zero_latitude(self):
        geo_elevation_data = mod_srtm.get_data()
        self.assertEquals(393, geo_elevation_data.get_elevation(0, 15))
        self.assertEquals(423, geo_elevation_data.get_elevation(-0.1, 15))
        self.assertEquals(381, geo_elevation_data.get_elevation(0.1, 15))

    def test_point_with_invalid_elevation(self):
        geo_elevation_data = mod_srtm.get_data()
        self.assertEquals(None, geo_elevation_data.get_elevation(47.0, 13.07))

    def test_point_without_file(self):
        geo_elevation_data = mod_srtm.get_data()
        print geo_elevation_data.get_elevation(0, 0)

    def test_files_equality(self):
        geo_elevation_data = mod_srtm.get_data()
        self.assertEquals(geo_elevation_data.get_file(47.0, 13.99),
                          geo_elevation_data.get_file(47.0, 13.0))
        self.assertEquals(geo_elevation_data.get_file(47.99, 13.99),
                          geo_elevation_data.get_file(47.0, 13.0))

        self.assertEquals(geo_elevation_data.get_file(-47.0, 13.99),
                          geo_elevation_data.get_file(-47.0, 13.0))
        self.assertEquals(geo_elevation_data.get_file(-47.99, 13.99),
                          geo_elevation_data.get_file(-47.0, 13.0))

        self.assertEquals(geo_elevation_data.get_file(-47.0, -13.99),
                          geo_elevation_data.get_file(-47.0, -13.0))
        self.assertEquals(geo_elevation_data.get_file(-47.99, -13.99),
                          geo_elevation_data.get_file(-47.0, -13.0))

        self.assertEquals(geo_elevation_data.get_file(47.0, -13.99),
                          geo_elevation_data.get_file(47.0, -13.0))
        self.assertEquals(geo_elevation_data.get_file(47.99, -13.99),
                          geo_elevation_data.get_file(47.0, -13.0))

    def test_invalit_coordinates_for_file(self):
        geo_elevation_data = mod_srtm.get_data()
        geo_file = geo_elevation_data.get_file(47.0, 13.99)

        try:
            self.assertFalse(geo_file.get_elevation(1, 1))
        except Exception as e:
            message = str(e)
            self.assertEquals('Invalid latitude 1 for file N47E013.hgt', message)

        try:
            self.assertFalse(geo_file.get_elevation(47, 1))
        except Exception as e:
            message = str(e)
            self.assertEquals('Invalid longitude 1 for file N47E013.hgt', message)

    def test_invalid_file(self):
        geo_elevation_data = mod_srtm.get_data()
        geo_file = geo_elevation_data.get_file(-47.0, -13.99)
        self.assertEquals(None, geo_file)

    def test_coordinates_in_file(self):
        geo_elevation_data = mod_srtm.get_data()
        geo_file = geo_elevation_data.get_file(47.0, 13.99)

        print 'file:', geo_file

        self.assertEquals(geo_file.get_elevation(47, 13),
                          geo_file.get_elevation(47, 13))

    def test_without_approximation(self):
        geo_elevation_data = mod_srtm.get_data()

        self.assertEquals(geo_elevation_data.get_elevation(47.1, 13.1, approximate=False),
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

        print elevation_without_approximation
        print elevation_with_approximation

        self.assertNotEquals(elevation_with_approximation, elevation_without_approximation)
        self.assertTrue(abs(elevation_with_approximation - elevation_without_approximation) < 30)
