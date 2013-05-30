# SRTM.py

SRTM.py is a python parser for the Shuttle Radar Topography Mission elevation data.

See: [http://www2.jpl.nasa.gov/srtm/](http://www2.jpl.nasa.gov/srtm/).

## Usage:

    >>> import srtm
    >>> elevation_data = srtm.get_data()
    >>> print 'CGN Airport elevation (meters):', elevation_data.get_elevation(50.8682, 7.1377)

You can create elevation images with:

    import srtm
    geo_elevation_data = srtm.get_data()
    image = geo_elevation_data.get_image((500, 500), (45, 46), (13, 14), 300)
    # the image s a standard PIL object, you can save or show it:
    image.show()

image.show()

## gpxelevations

**TODO**

## License

GPX.py is licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)

