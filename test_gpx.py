# -*- coding: utf-8 -*-

import gpxpy as mod_gpxpy

import srtm.retriever  as mod_retriever

with open('giro-del-horizonte-2013.gpx') as f:
    gpx_contents = f.read()

gpx = mod_gpxpy.parse(gpx_contents)

geo_elevation_data = mod_retriever.get_geo_elevation_data()

for segment_no, segment in enumerate(gpx.tracks[0].segments):
    for point in segment.points:
        calculated = geo_elevation_data.get_elevation(point.latitude, point.longitude)
        print 'segment #%s (%13s, %13s) -> gpx:%10s calculated:%10s' % (segment_no, point.latitude, point.longitude, point.elevation, calculated)
