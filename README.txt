Shuttle Radar Topography Mission elevation data python parser and utilities

See: http://www2.jpl.nasa.gov/srtm/

Usage:

>>> import srtm
>>> get_data = srtm.get_data()
>>> print 'CGN Airport elevation (meters):', get_data.get_elevation(50.8682, 7.1377)
