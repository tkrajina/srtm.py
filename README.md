# SRTM.py

SRTM.py is a python parser for the Shuttle Radar Topography Mission elevation data.

See: [http://www2.jpl.nasa.gov/srtm/](http://www2.jpl.nasa.gov/srtm/).

## Usage:

    import srtm
    elevation_data = srtm.get_data()
    print 'CGN Airport elevation (meters):', elevation_data.get_elevation(50.8682, 7.1377)

With get\_elevation() an elevation of the the nearest location found in the SRTM data will be given.
If you need an approximation based on nearby locations, you can use:

    elevation_data.get_elevation(50.8682, 7.1377, approximate=True)

You can create elevation images with:

    import srtm
    geo_elevation_data = srtm.get_data()
    image = geo_elevation_data.get_image((500, 500), (45, 46), (13, 14), 300)
    # the image s a standard PIL object, you can save or show it:
    image.show()

On every elevation requested the library will:

 * Check if the SRTM file is stored locally
 * If not -- download it from NASA servers
 * Parse elevations from it

That's why the first run of your application will always take a few seconds.

### Example images

Istra and Trieste:

![Istra](http://tkrajina.github.io/srtm.py/istra.png)

Rio de Janeiro:

![Rio](http://tkrajina.github.io/srtm.py/rio.png)

Miami and florida:

![Miami](http://tkrajina.github.io/srtm.py/miami.png)

Sidney:

![Sidney](http://tkrajina.github.io/srtm.py/sidney.png)

## gpxelevations

gpxelevations is a utility commandline tool to add/update elevations in a GPS track file:

    $ gpxelevations -h
    usage: gpxelevations [-h] [-o] [-p] [-s] [-c] [-f FILE] [-v]
                         [gpx_files [gpx_files ...]]

    Adds elevation to GPX files

    positional arguments:
      gpx_files             GPX files

    optional arguments:
      -h, --help            show this help message and exit
      -o, --overwrite       Overwrite existing elevations (otherwise will add
                            elevations only where not yet present)
      -p, --approximate     Approximate elevations with neighbour point elevations
      -s, --smooth          Smooth elevations
      -c, --calculate       Calculate elevations (but don't change the GPX file
      -f FILE, --file FILE  Output filename
      -v, --verbose         Verbose output

## License

GPX.py is licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)

