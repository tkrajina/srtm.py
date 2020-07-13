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

import logging        as mod_logging
import unittest       as mod_unittest
import srtm           as mod_srtm
from srtm import data as mod_data
from srtm import main as mod_main
from srtm import utils as mod_utils

mod_logging.basicConfig(level=mod_logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

class Tests(mod_unittest.TestCase):

    def test_dead_sea(self) -> None:
        geo_elevation_data = mod_srtm.get_data()
        self.assertEqual(-415, geo_elevation_data.get_elevation(31.5, 35.5))

    def test_over_60(self) -> None:
        geo_elevation_data = mod_srtm.get_data()
        self.assertTrue(geo_elevation_data.get_elevation(55., 55.) > 0) # type: ignore
        self.assertEqual(None, geo_elevation_data.get_elevation(65., 65.))
        self.assertEqual(None, geo_elevation_data.get_elevation(75., 75.))

    def test_random_points(self) -> None:
        geo_elevation_data = mod_srtm.get_data()
        self.assertEqual(63, geo_elevation_data.get_elevation(46., 13.))
        self.assertEqual(2714, geo_elevation_data.get_elevation(46.999999, 13.))
        self.assertEqual(1643, geo_elevation_data.get_elevation(46.999999, 13.999999))
        self.assertEqual(553, geo_elevation_data.get_elevation(46., 13.999999))
        self.assertEqual(203, geo_elevation_data.get_elevation(45.2732, 13.7139))
        self.assertEqual(460, geo_elevation_data.get_elevation(45.287, 13.905))

    def test_around_zero_longitude(self) -> None:
        geo_elevation_data = mod_srtm.get_data()
        self.assertEqual(61, geo_elevation_data.get_elevation(51.2, 0.0))
        self.assertEqual(100, geo_elevation_data.get_elevation(51.2, -0.1))
        self.assertEqual(59, geo_elevation_data.get_elevation(51.2, 0.1))

    def test_around_zero_latitude(self) -> None:
        geo_elevation_data = mod_srtm.get_data()
        self.assertEqual(393, geo_elevation_data.get_elevation(0, 15))
        self.assertEqual(423, geo_elevation_data.get_elevation(-0.1, 15))
        self.assertEqual(381, geo_elevation_data.get_elevation(0.1, 15))

    def test_point_with_invalid_elevation(self) -> None:
        geo_elevation_data = mod_srtm.get_data()
        self.assertEqual(None, geo_elevation_data.get_elevation(47.0, 13.07))

    def test_point_without_file(self) -> None:
        geo_elevation_data = mod_srtm.get_data()
        print(geo_elevation_data.get_elevation(0, 0))

    def test_files_equality(self) -> None:
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

    def test_invalit_coordinates_for_file(self) -> None:
        geo_elevation_data = mod_srtm.get_data()
        geo_file = geo_elevation_data.get_file(47.0, 13.99)

        try:
            self.assertFalse(geo_file.get_elevation(1, 1)) # type: ignore
        except Exception as e:
            message = str(e)
            self.assertEqual('Invalid latitude 1 for file N47E013.hgt', message)

        try:
            self.assertFalse(geo_file.get_elevation(47, 1)) # type: ignore
        except Exception as e:
            message = str(e)
            self.assertEqual('Invalid longitude 1 for file N47E013.hgt', message)

    def test_invalid_file(self) -> None:
        geo_elevation_data = mod_srtm.get_data()
        geo_file = geo_elevation_data.get_file(-47.0, -13.99)
        self.assertEqual(None, geo_file)

    def test_coordinates_in_file(self) -> None:
        geo_elevation_data = mod_srtm.get_data()
        geo_file = geo_elevation_data.get_file(47.0, 13.99)

        print('file:', geo_file)

        self.assertEqual(geo_file.get_elevation(47, 13), geo_file.get_elevation(47, 13)) # type: ignore

    def test_coordinates_row_col_conversion(self) -> None:
        geo_elevation_data = mod_srtm.get_data()
        geo_file = geo_elevation_data.get_file(47.0, 13.99)

        print('file:', geo_file)

        r, c = geo_file.get_row_and_column(47, 13) # type: ignore
        lat, long = geo_file.get_lat_and_long(r, c) # type: ignore
        self.assertEqual(lat, 47)
        self.assertEqual(long, 13)

        r, c = geo_file.get_row_and_column(46.5371, 8.1264) # type: ignore
        lat, long = geo_file.get_lat_and_long(r, c) # type: ignore
        self.assertAlmostEqual(lat, 46.5371, delta=geo_file.resolution) # type: ignore
        self.assertAlmostEqual(long, 8.1264, delta=geo_file.resolution) # type: ignore

    def test_without_approximation(self) -> None:
        geo_elevation_data = mod_srtm.get_data()

        self.assertEqual(geo_elevation_data.get_elevation(47.1, 13.1, approximate=False),
                          geo_elevation_data.get_elevation(47.1, 13.1))

        # SRTM elevations are always integers:
        elevation = geo_elevation_data.get_elevation(47.1, 13.1)
        self.assertTrue(int(elevation) == elevation) # type: ignore

    def test_with_approximation(self) -> None:
        geo_elevation_data = mod_srtm.get_data()

        self.assertNotEquals(geo_elevation_data.get_elevation(47.1, 13.1, approximate=True),
                             geo_elevation_data.get_elevation(47.1, 13.1))

        # When approximating a random point, it probably won't be a integer:
        elevation = geo_elevation_data.get_elevation(47.1, 13.1, approximate=True)
        self.assertTrue(int(elevation) != elevation) # type: ignore

    def test_approximation(self) -> None:
        # TODO(TK) Better tests for approximation here:
        geo_elevation_data = mod_srtm.get_data()
        elevation_without_approximation = geo_elevation_data.get_elevation(47, 13)
        elevation_with_approximation = geo_elevation_data.get_elevation(47, 13, approximate=True)

        print(elevation_without_approximation)
        print(elevation_with_approximation)

        self.assertNotEqual(elevation_with_approximation, elevation_without_approximation)
        self.assertTrue(abs(elevation_with_approximation - elevation_without_approximation) < 30) # type: ignore

    def test_IDW(self) -> None:
        print("Testing: IDW")

        # Setup with local tile
        with open("test_files/N44W072.hgt","rb") as hgtfile:
            hgt = hgtfile.read()
        tilemap = mod_data.GeoElevationData({},{}, file_handler=mod_utils.FileHandler(""))
        tile = mod_data.GeoElevationFile('N44W072.hgt', hgt, tilemap)
        tilemap.srtm3_files["N44W072.hgt"] = ""
        tilemap.files["N44W072.hgt"] = tile
        lat, long = 44.1756325, -71.5965699
        elevation = tilemap._IDW(lat, long)
        print("Location: {}, {}".format(lat, long))
        print("Elevation: {}".format(elevation))
        print()
        self.assertLessEqual(elevation, 814)
        self.assertGreaterEqual(elevation, 801)
        self.assertTrue(tilemap._IDW(-47.0, -13.99) is None)
        

    def test_InverseDistanceWeighted(self) -> None:
        print("Testing: InverseDistanceWeighted")

        # Setup minimal tile config
        with open("test_files/N44W072.hgt","rb") as hgtfile:
            hgt = hgtfile.read()
        tilemap = mod_data.GeoElevationData({},{}, file_handler=mod_utils.FileHandler())
        tile = mod_data.GeoElevationFile('N44W072.hgt', hgt, tilemap)

        # tuples of (lat, lon, lowerbound, upperbound)
        controlpoints = [(44.1756325, -71.5965699, 801, 814), # middle of tile (x,y)
                         (44, -71.5965699, 520, 532), # bottom edge (1200, y)
                         (44.1756325, -70.99975, 148, 152), # right edge (x, 1200)
                         (44.99975, -71.5965699, 525, 538), # top edge (0, y)
                         (44.1756325, -71.99975, 272, 279), # left edge (x, 0)
                         (44, -72, 341, 341)] # Exact cell coordinates, no interpolation

        for location in controlpoints:
            print("Location: {}, {}".format(location[0], location[1]))
            nearest_neighbor_elevation = tile.get_elevation(location[0], location[1])
            IDW5_elevation = tile._InverseDistanceWeighted(location[0], location[1])
            IDW13_elevation = tile._InverseDistanceWeighted(location[0], location[1], radius=2)
            print("Nearest: " + str(nearest_neighbor_elevation))
            print("Interpolated(5): {}".format(IDW5_elevation))
            print("Interpolated(13): {}".format(IDW13_elevation))
            print()
            self.assertGreaterEqual(IDW5_elevation, location[2])
            self.assertLessEqual(IDW5_elevation, location[3])
            self.assertGreaterEqual(IDW13_elevation, location[2])
            self.assertLessEqual(IDW13_elevation, location[3])

        self.assertRaises(ValueError, tile._InverseDistanceWeighted, 44, -71, radius=0)
            

    def test_batch_mode(self) -> None:
        
        # Two pulls that are far enough apart to require multiple files

        # With batch_mode=False, both files should be kept
        geo_elevation_data = mod_srtm.get_data(batch_mode=False)

        elevation1 = geo_elevation_data.get_elevation(42.3467, 71.0972)
        self.assertTrue(elevation1 > 0) # type: ignore
        self.assertTrue(len(geo_elevation_data.files) == 1)

        elevation2 = geo_elevation_data.get_elevation(43.0382, 87.9298)
        self.assertTrue(elevation2 > 0) # type: ignore
        self.assertTrue(len(geo_elevation_data.files) == 2)

        # With batch_mode=True, only the most recent file should be kept
        geo_elevation_data = mod_srtm.get_data(batch_mode=True)
        elevation1 = geo_elevation_data.get_elevation(42.3467, 71.0972)
        self.assertTrue(elevation1 > 0) # type: ignore
        self.assertTrue(len(geo_elevation_data.files) == 1)
        keys1 = geo_elevation_data.files.keys()

        elevation2 = geo_elevation_data.get_elevation(43.0382, 87.9298)
        self.assertTrue(len(geo_elevation_data.files) == 1)
        self.assertFalse(geo_elevation_data.files.keys() == keys1)


if __name__ == '__main__':
    mod_unittest.main()
