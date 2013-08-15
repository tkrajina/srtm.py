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

import gpxpy.gpx as mod_gpx

from . import main as mod_srtm

def add_elevations(gpx, smooth=False, gpx_smooth_no=0):
    elevation_data = mod_srtm.get_data()
    if smooth:
        add_sampled_elevations(gpx)
    else:
        for point in gpx.walk(only_points=True):
            point.elevation = elevation_data.get_elevation(point.latitude, point.longitude)

    for i in range(gpx_smooth_no):
        gpx.smooth(vertical=True, horizontal=False)

def add_interval_elevations(gpx, min_interval_length=100):
    """
    Adds elevation on points every min_interval_length and add missing 
    elevation between
    """
    elevation_data = mod_srtm.get_data()
    last_interval_changed = 0
    for track in gpx.tracks:
        for segment in track.segments:
            previous_point = None
            length = 0
            for no, point in enumerate(segment.points):
                if previous_point:
                    length += point.distance_2d(previous_point)

                if no == 0 or no == len(segment.points) - 1 or length > last_interval_changed:
                    last_interval_changed += min_interval_length
                    point.elevation = elevation_data.get_elevation(point.latitude, point.longitude)
                else:
                    point.elevation = None
                previous_point = point
    gpx.add_missing_elevations()

def add_sampled_elevations(gpx):
    # Use some random intervals here to randomize a bit:
    add_interval_elevations(gpx, min_interval_length=35)
    elevations_1 = list(map(lambda point: point.elevation, gpx.walk(only_points=True)))
    add_interval_elevations(gpx, min_interval_length=141)
    elevations_2 = list(map(lambda point: point.elevation, gpx.walk(only_points=True)))
    add_interval_elevations(gpx, min_interval_length=241)
    elevations_3 = list(map(lambda point: point.elevation, gpx.walk(only_points=True)))

    n = 0
    for point in gpx.walk(only_points=True):
        if elevations_1[n] != None and elevations_2[n] != None and elevations_3[n] != None:
            #print elevations_1[n], elevations_2[n], elevations_3[n]
            point.elevation = (elevations_1[n] + elevations_2[n] + elevations_3[n]) / 3.
        else:
            point.elevation = None
        n += 1

