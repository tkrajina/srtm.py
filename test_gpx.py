# -*- coding: utf-8 -*-

"""
Example on how to add elevations to existing GPX file
"""

import gpxpy as mod_gpxpy

import srtm as mod_srtm

gpx_contents = """<?xml version="1.0"?><gpx creator="GPS Visualizer http://www.gpsvisualizer.com/" version="1.0" xmlns="http://www.topografix.com/GPX/1/0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd"><trk><name>test</name><trkseg><trkpt lat="47.0" lon="13.0"><ele>2714.0</ele></trkpt><trkpt lat="47.01" lon="13.0"><ele>2652.0</ele></trkpt><trkpt lat="47.02" lon="13.0"></trkpt><trkpt lat="47.03" lon="13.0"><ele>2414.0</ele></trkpt><trkpt lat="47.04" lon="13.0"><ele>2679.0</ele></trkpt><trkpt lat="47.05" lon="13.0"><ele>2710.0</ele></trkpt><trkpt lat="47.06" lon="13.0"><ele>2145.0</ele></trkpt><trkpt lat="47.07" lon="13.0"><ele>2004.0</ele></trkpt><trkpt lat="47.08" lon="13.0"><ele>1782.0</ele></trkpt><trkpt lat="47.09" lon="13.0"><ele>1592.0</ele></trkpt></trkseg><trkseg><trkpt lat="47.0" lon="13.0"><ele>2714.0</ele></trkpt><trkpt lat="47.0" lon="13.01"><ele>2522.0</ele></trkpt><trkpt lat="47.0" lon="13.02"><ele>2421.0</ele></trkpt><trkpt lat="47.0" lon="13.03"><ele>2099.0</ele></trkpt><trkpt lat="47.0" lon="13.04"><ele>1689.0</ele></trkpt><trkpt lat="47.0" lon="13.05"><ele>2080.0</ele></trkpt><trkpt lat="47.0" lon="13.06"><ele>2279.0</ele></trkpt><trkpt lat="47.0" lon="13.07"></trkpt><trkpt lat="47.0" lon="13.08"><ele>2343.0</ele></trkpt><trkpt lat="47.0" lon="13.09"><ele>1973.0</ele></trkpt></trkseg></trk></gpx>"""

gpx = mod_gpxpy.parse(gpx_contents)

geo_elevation_data = mod_srtm.get_data()

for segment_no, segment in enumerate(gpx.tracks[0].segments):
    for point in segment.points:
        calculated = geo_elevation_data.get_elevation(point.latitude, point.longitude)
        print 'segment #%s (%13s, %13s) -> gpx:%10s calculated:%10s' % (segment_no, point.latitude, point.longitude, point.elevation, calculated)
