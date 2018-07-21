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

import json     as mod_json
import warnings as mod_warnings

from . import data      as mod_data
from . import retriever as mod_retriever

# Deprecated URLs
SRTM1_URL = 'http://dds.cr.usgs.gov/srtm/version2_1/SRTM1/'
SRTM3_URL = 'http://dds.cr.usgs.gov/srtm/version2_1/SRTM3/'


def get_data(srtm1=None, srtm3=None, version='v2.1a', fallback=True,
             leave_zipped=False, file_handler=None,
             use_included_urls=True, batch_mode=False):
    """
    Get the utility object for querying elevation data.

    All data files will be stored in local cache (note that it may be
    gigabytes of data so clean it from time to time).

    version (str) options are-
        v1.1a, v1.3a, v2.1a, v2.3a, v2.3as, v3.1a, v3.3a, v3.3as
        See GeoElevationData.__init__ docstring for more detail
        
    fallback (bool) determines whether to try the next version if
    get_elevation fails. See GeoElevationData.fallback_version docstring
    for more detail
        
    If you need to change the way the files are saved locally (for example if
    you need to save them locally) -- change the file_handler. See
    srtm.data.FileHandler.

    If leave_zipped is True then files will be stored locally as compressed
    zip files. That means less disk space but more computing space for every
    file loaded.

    If batch_mode is True, only the most recent file will be stored. This is
    ideal for situations where you want to use this function to enrich a very
    large dataset. If your data are spread over a wide geographic area, this
    setting will make this function slower but will greatly reduce the risk
    of out-of-memory errors. Default is False.

    *** Deprecated below here *** Replaced with version and fallback ***
    If use_included_urls is True urls to SRTM files included in the library
    will be used. Set to false if you need to reload them on first run.

    With srtm1 or srtm3 params you can decide which SRTM format to use. Srtm3
    has a resolution of three arc-seconds (cca 90 meters between points).
    Srtm1 has a resolution of one arc-second (cca 30 meters). Srtm1 is
    available only for the United states. If both srtm1 and srtm3 are True and
    both files are present for a location -- the srtm1 will be used.
    ********************************************************************
    """

    if srtm1 or srtm3:
        mod_warnings.warn("Use of srtm1_files and srtm3_files is deprecated. Use version instead", DeprecationWarning)

    if file_handler is None:
        file_handler = mod_data.FileHandler()

    srtm1_files, srtm3_files = _get_urls(use_included_urls, file_handler)

    if not srtm1: srtm1_files = {}
    if not srtm3: srtm3_files = {}

    return mod_data.GeoElevationData(srtm1_files, srtm3_files, file_handler=file_handler,
                                     leave_zipped=leave_zipped, batch_mode=batch_mode)

def _get_urls(use_included_urls, file_handler):
    files_list_file_name = 'list.json'
    try:
        urls_json = _get_urls_json(use_included_urls, file_handler)
        return urls_json['srtm1'], urls_json['srtm3']
    except:
        srtm1_files = mod_retriever.retrieve_all_files_urls(SRTM1_URL)
        srtm3_files = mod_retriever.retrieve_all_files_urls(SRTM3_URL)

        file_handler.write(files_list_file_name,
                           mod_json.dumps({'srtm1': srtm1_files, 'srtm3': srtm3_files}, sort_keys=True, indent=4))

        return srtm1_files, srtm3_files

def _get_urls_json(use_included_urls, file_handler):
    if use_included_urls:
        with open(mod_data.DEFAULT_LIST_JSON, 'r') as f:
            return mod_json.loads(f.read())

    files_list_file_name = 'list.json'
    contents = file_handler.read(files_list_file_name)
    return mod_json.loads(contents)

