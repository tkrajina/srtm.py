# -*- coding: utf-8 -*-

import gpxpy.gpx as mod_gpx

start_latitude = 47.0
start_longitude = 13.0

gpx = mod_gpx.GPX() 

track = mod_gpx.GPXTrack()

segment_1 = mod_gpx.GPXTrackSegment()
segment_2 = mod_gpx.GPXTrackSegment()

for i in range(0, 10):
    d = i * 0.01
    segment_1.points.append(mod_gpx.GPXTrackPoint(start_latitude + d, start_longitude    ))
    segment_2.points.append(mod_gpx.GPXTrackPoint(start_latitude    , start_longitude + d))

track.segments.append(segment_1)
track.segments.append(segment_2)

gpx.tracks.append(track)

print gpx.to_xml()

file_name = 'test.gpx'
with open(file_name, 'w') as f:
    f.write(gpx.to_xml())
    print 'Written to %s' % file_name
