# -*- coding: utf-8 -*-

import logging        as mod_logging
import os             as mod_os
import urllib         as mod_urllib
import re             as mod_re
import pickle         as mod_pickle
import os.path        as mod_path

import data           as mod_data

# Local cache path:
LOCAL_FILES_DIRECTORY = '{0}/.geo_elevation_files'.format(mod_os.environ['HOME'])

if not mod_path.exists(LOCAL_FILES_DIRECTORY):
    mod_os.makedirs(LOCAL_FILES_DIRECTORY)

FILES_LOCATION = '{0}/list'.format(LOCAL_FILES_DIRECTORY)

SRTM1_URL = 'http://dds.cr.usgs.gov/srtm/version2_1/SRTM1/'
SRTM3_URL = 'http://dds.cr.usgs.gov/srtm/version2_1/SRTM3/'

def get_geo_elevation_data():
    """
    Load the urls of all geo-elevation files. If it can't be found -- it wil 
    retrieve it and save to LOCAL_FILES_DIRECTORY.
    """
    try:
        f = open(FILES_LOCATION, 'r')
        contents = f.read()
        f.close()

        urls = mod_pickle.loads(contents)

        srtm1_files = urls['srtm1']
        srtm3_files = urls['srtm3']
    except:
        srtm1_files = retrieve_all_files_urls(SRTM1_URL)
        srtm3_files = retrieve_all_files_urls(SRTM3_URL)

        f = open(FILES_LOCATION, 'w')
        f.write(mod_pickle.dumps({'srtm1': srtm1_files, 'srtm3': srtm3_files}))
        f.close()

    assert srtm1_files
    assert srtm3_files

    return mod_data.GeoElevationData(srtm1_files, srtm3_files)

def retrieve_all_files_urls(url):
    mod_logging.info('Retrieving {0}'.format(url))
    url_stream = mod_urllib.urlopen(url)
    contents = url_stream.read()
    url_stream.close()

    url_candidates = mod_re.findall('href="(.*?)"', contents)
    urls = {}

    for url_candidate in url_candidates:
        if url_candidate.endswith('/') and not url_candidate in url:
            files_url = '{0}/{1}'.format(url, url_candidate)

            urls.update(get_files(files_url))

    return urls
	
def get_files(url):
    mod_logging.info('Retrieving {0}'.format(url))
    url_stream = mod_urllib.urlopen(url)
    contents = url_stream.read()
    url_stream.close()

    result = {}

    url_candidates = mod_re.findall('href="(.*?)"', contents)
    for url_candidate in url_candidates:
        if url_candidate.endswith('.hgt.zip'):
            file_url = '{0}/{1}'.format(url, url_candidate)
            result[url_candidate.replace('.zip', '')] = file_url

    mod_logging.info('Found {0} files'.format(len(result)))

    return result

if __name__ == '__main__':
    latitude = 45.
    longitude = 45.

    print get_geo_elevation_data()

