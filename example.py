import srtm

elevation_data = srtm.get_data(local_cache_dir="tmp_cache")
print('CGN Airport elevation (meters):', elevation_data.get_elevation(50.8682, 7.1377))

elevation_data_with_custom_dir = srtm.get_data(local_cache_dir="tmp_cache")
print('CGN Airport elevation (meters):', elevation_data_with_custom_dir.get_elevation(50.8682, 7.1377))