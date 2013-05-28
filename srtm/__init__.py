# -*- coding: utf-8 -*-

# Copyright 2013 Tomo Krajina
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import cPickle  as mod_pickle
import os       as mod_os
import os.path  as mod_path

from . import data      as mod_data
from . import retriever as mod_retriever

# Local cache path:
LOCAL_FILES_DIRECTORY = '{0}/.geo_elevation_files'.format(mod_os.environ['HOME'])

if not mod_path.exists(LOCAL_FILES_DIRECTORY):
    mod_os.makedirs(LOCAL_FILES_DIRECTORY)

FILES_LOCATION = '{0}/list'.format(LOCAL_FILES_DIRECTORY)

SRTM1_URL = 'http://dds.cr.usgs.gov/srtm/version2_1/SRTM1/'
SRTM3_URL = 'http://dds.cr.usgs.gov/srtm/version2_1/SRTM3/'

def get_data():
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
        srtm1_files = mod_retriever.retrieve_all_files_urls(SRTM1_URL)
        srtm3_files = mod_retriever.retrieve_all_files_urls(SRTM3_URL)

        f = open(FILES_LOCATION, 'w')
        f.write(mod_pickle.dumps({'srtm1': srtm1_files, 'srtm3': srtm3_files}))
        f.close()

    assert srtm1_files
    assert srtm3_files

    return mod_data.GeoElevationData(srtm1_files, srtm3_files, LOCAL_FILES_DIRECTORY)
