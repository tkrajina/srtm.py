import gpxpy as mod_gpxpy
import cartesius.main as mod_cartesius
import cartesius.charts as mod_charts
import cartesius.elements as mod_elements
import logging as mod_logging
import srtm.gpx as mod_srtmgpx

mod_logging.basicConfig(level=mod_logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

def get_line(gpx, color):
    def f():
        previous_point = None
        length = 0
        for point in gpx.walk(only_points=True):
            if previous_point:
                length += previous_point.distance_2d(point)
            previous_point = point
            yield mod_charts.data(length, point.elevation)

    return mod_charts.LineChart(data=f, color=color)

def sample_gpx():
    return mod_gpxpy.parse(open('sample_files/setnjica-kod-karojbe.gpx'))

coordinate_system = mod_cartesius.CoordinateSystem(bounds=(-150, 2800, -30, 450))

coordinate_system.add(mod_elements.Grid(20, 100))

gpx = sample_gpx()
coordinate_system.add(get_line(gpx, color=(0, 0, 0)))

gpx = sample_gpx()
mod_srtmgpx.add_elevations(gpx)
coordinate_system.add(get_line(gpx, color=(0, 0, 255)))

gpx = sample_gpx()
mod_srtmgpx.add_elevations(gpx, smooth=True)
coordinate_system.add(get_line(gpx, color=(255, 0, 0)))

coordinate_system.add(mod_elements.Axis(horizontal=True, labels=250, points=50))
coordinate_system.add(mod_elements.Axis(vertical=True, labels=50, points=10))

image = coordinate_system.draw(600, 400, antialiasing=True)

image.save('gpx_elevations.png')
