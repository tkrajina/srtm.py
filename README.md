# SRTM.py

SRTM.py is a python parser for the Shuttle Radar Topography Mission elevation data.

See: [http://www2.jpl.nasa.gov/srtm/](http://www2.jpl.nasa.gov/srtm/).

## Usage:

    >>> import srtm
    >>> elevation_data = srtm.get_data()
    >>> print 'CGN Airport elevation (meters):', elevation_data.get_elevation(50.8682, 7.1377)

## gpxelevations

**TODO**

## License

GPX.py is licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)

