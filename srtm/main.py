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
import os       as mod_os
import os.path  as mod_path

from . import data      as mod_data
from . import retriever as mod_retriever
from . import utils     as mod_utils

from typing import *

SRTM1_URL = 'https://srtm.kurviger.de/SRTM1/'
SRTM3_URL = 'https://srtm.kurviger.de/SRTM3/'

package_location = mod_data.__file__[: mod_data.__file__.rfind(mod_path.sep)]
DEFAULT_LIST_JSON = package_location + mod_os.sep + 'list.json'

def get_data(srtm1: bool=True, srtm3: bool=True, leave_zipped: bool=False, file_handler: Optional[mod_utils.FileHandler]=None,
             use_included_urls: bool=True, batch_mode: bool=False, local_cache_dir: str = "", timeout: int = 0) -> mod_data.GeoElevationData:
    """
    Get the utility object for querying elevation data.

    All data files will be stored in localy (note that it may be
    gigabytes of data so clean it from time to time).

    On first run -- all files needed url will be stored and for every next
    elevation query if the SRTM file is not found it will be retrieved and
    saved.

    If you need to change the way the files are saved locally (for example if
    you need to save them locally) -- change the file_handler. See
    srtm.main.FileHandler.

    If leave_zipped is True then files will be stored locally as compressed
    zip files. That means less disk space but more computing space for every
    file loaded.

    If use_included_urls is True urls to SRTM files included in the library
    will be used. Set to false if you need to reload them on first run.

    If batch_mode is True, only the most recent file will be stored. This is
    ideal for situations where you want to use this function to enrich a very
    large dataset. If your data are spread over a wide geographic area, this
    setting will make this function slower but will greatly reduce the risk
    of out-of-memory errors. Default is False.

    With srtm1 or srtm3 params you can decide which SRTM format to use. Srtm3
    has a resolution of three arc-seconds (cca 90 meters between points).
    Srtm1 has a resolution of one arc-second (cca 30 meters). Srtm1 is
    available only for the United states. If both srtm1 ans srtm3 are True and
    both files are present for a location -- the srtm1 will be used.
    """
    if not file_handler:
        file_handler = mod_utils.FileHandler(local_cache_dir)

    if not srtm1 and not srtm3:
        raise Exception('At least one of srtm1 and srtm3 must be True')

    srtm1_files, srtm3_files = _get_urls(use_included_urls, file_handler, timeout)

    assert srtm1_files
    assert srtm3_files

    if not srtm1:
        srtm1_files = {}
    if not srtm3:
        srtm3_files = {}

    assert srtm1_files or srtm3_files

    return mod_data.GeoElevationData(srtm1_files, srtm3_files, file_handler=file_handler,
                                     leave_zipped=leave_zipped, batch_mode=batch_mode,
                                     timeout=timeout)

def _get_urls(use_included_urls: bool, file_handler: mod_utils.FileHandler, timeout: int) -> Tuple[Dict[str, str], Dict[str, str]]:
    files_list_file_name = 'list.json'
    try:
        urls_json = _get_urls_json(use_included_urls, file_handler)
        return urls_json['srtm1'], urls_json['srtm3']
    except:
        srtm1_files = mod_retriever.retrieve_all_files_urls(SRTM1_URL, timeout)
        srtm3_files = mod_retriever.retrieve_all_files_urls(SRTM3_URL, timeout)

        file_handler.write(files_list_file_name, mod_json.dumps({'srtm1': srtm1_files, 'srtm3': srtm3_files}, sort_keys=True, indent=4).encode())

        return srtm1_files, srtm3_files

def _get_urls_json(use_included_urls: bool, file_handler: mod_utils.FileHandler) -> Any:
    if use_included_urls:
        with open(DEFAULT_LIST_JSON, 'r') as f:
            return mod_json.loads(f.read())

    files_list_file_name = 'list.json'
    contents = file_handler.read(files_list_file_name)
    return mod_json.loads(contents)