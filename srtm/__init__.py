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

import pdb

import json     as mod_json
import os       as mod_os
import os.path  as mod_path

from . import data      as mod_data
from . import retriever as mod_retriever

SRTM1_URL = 'http://dds.cr.usgs.gov/srtm/version2_1/SRTM1/'
SRTM3_URL = 'http://dds.cr.usgs.gov/srtm/version2_1/SRTM3/'

def get_default_srtm_dir():
    """ The default path to store files. """
    # Local cache path:
    if not mod_os.environ.has_key('HOME'):
        raise Error('No default HOME directory found, please specify a path where to store files')

    result = '{0}/.srtm'.format(mod_os.environ['HOME'])

    if not mod_path.exists(result):
        mod_os.makedirs(result)

    return result

def get_data(local_srtm_dir=None, reduce_big_files=False, leave_zipped=False):
    """
    Get the utility object for querying elevation data.

    All data files will be stored in local_srtm_dir (note that it may be 
    gigabytes of data so clean it from time to time).

    On first run -- all files url will be stored and for every next elevation 
    query if the SRTM file is not found in local_srtm_dir it will be retrieved 
    and saved.

    If reduce_big_files is True files for north America will be reduced to the 
    same size as the rest of the world. It may be used to save disk space 
    (because otherwise the tipical USA file is 25 megabaytes comparet to 2-3 
    megabytes for the rest).

    If leave_zipped is True then files will be stored locally as compressed 
    zip files. That means less disk space but more computing space for every 
    file loaded. Note that if you leave this to True and don't reduce big 
    files -- unzipping them on runtime will be slow.
    """
    if not local_srtm_dir:
        local_srtm_dir = get_default_srtm_dir()

    if not local_srtm_dir:
        raise Error('Please specify a path where to store files')

    files_list_file_name = '{0}/list.json'.format(local_srtm_dir)
    try:
        f = open(files_list_file_name, 'r')
        contents = f.read()
        f.close()

        urls = mod_json.loads(contents)

        srtm1_files = urls['srtm1']
        srtm3_files = urls['srtm3']
    except:
        srtm1_files = mod_retriever.retrieve_all_files_urls(SRTM1_URL)
        srtm3_files = mod_retriever.retrieve_all_files_urls(SRTM3_URL)

        f = open(files_list_file_name, 'w')
        f.write(mod_json.dumps({'srtm1': srtm1_files, 'srtm3': srtm3_files},
                               sort_keys=True, indent=4))
        f.close()

    assert srtm1_files
    assert srtm3_files

    return mod_data.GeoElevationData(srtm1_files, srtm3_files, local_srtm_dir,
                                     reduce_big_files=reduce_big_files,
                                     leave_zipped=leave_zipped)
