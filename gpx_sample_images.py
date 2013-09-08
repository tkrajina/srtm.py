import gpxpy as mod_gpxpy
import cartesius.main as mod_cartesius
import cartesius.charts as mod_charts
import cartesius.elements as mod_elements
import logging as mod_logging
import srtm as mod_srtm

mod_logging.basicConfig(level=mod_logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

def get_line(gpx, color, transparency_mask=None):
    def f():
        previous_point = None
        length = 0
        for point in gpx.walk(only_points=True):
            if previous_point:
                length += previous_point.distance_2d(point)
            previous_point = point
            yield mod_charts.data(length, point.elevation if point.elevation != None else 0)

    return mod_charts.LineChart(data=f, color=color, transparency_mask=transparency_mask)

def sample_gpx():
    return mod_gpxpy.parse(open('sample_files/grmada.gpx'))

coordinate_system = mod_cartesius.CoordinateSystem(bounds=(-300, 50000, -40, 1000))

coordinate_system.add(mod_elements.Grid(20, 100))

gpx = sample_gpx()
coordinate_system.add(get_line(gpx, color=(0, 0, 0)))

data = mod_srtm.get_data()

gpx = sample_gpx()
data.add_elevations(gpx)
coordinate_system.add(get_line(gpx, color=(0, 0, 255), transparency_mask=150))

gpx = sample_gpx()
data.add_elevations(gpx, smooth=True)
coordinate_system.add(get_line(gpx, color=(255, 0, 0)))

coordinate_system.add(mod_elements.Axis(horizontal=True, labels=500, points=100))
coordinate_system.add(mod_elements.Axis(vertical=True, labels=100, points=20))

image = coordinate_system.draw(600, 400, antialiasing=True)
#image.show()

image.show()
