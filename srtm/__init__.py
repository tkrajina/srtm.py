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
from . import utils     as mod_utils
from . import retriever as mod_retriever

SRTM1_URL = 'http://dds.cr.usgs.gov/srtm/version2_1/SRTM1/'
SRTM3_URL = 'http://dds.cr.usgs.gov/srtm/version2_1/SRTM3/'

def get_data(reduce_big_files=False, leave_zipped=False, file_handler=None):
    """
    Get the utility object for querying elevation data.

    All data files will be stored in localy (note that it may be 
    gigabytes of data so clean it from time to time).

    On first run -- all files needed url will be stored and for every next 
    elevation query if the SRTM file is not found it will be retrieved and 
    saved.

    If you need to change the way the files are saved locally (for example if 
    you need to save them locally) -- change the file_handler. See 
    srtm.utils.FileHandler.

    If reduce_big_files is True files for north America will be reduced to the 
    same size as the rest of the world. It may be used to save disk space 
    (because otherwise the tipical USA file is 25 megabaytes comparet to 2-3 
    megabytes for the rest).

    If leave_zipped is True then files will be stored locally as compressed 
    zip files. That means less disk space but more computing space for every 
    file loaded. Note that if you leave this to True and don't reduce big 
    files -- unzipping them on runtime will be slow.
    """
    if not file_handler:
        file_handler = FileHandler()

    files_list_file_name = 'list.json'
    try:
        contents = file_handler.read(files_list_file_name)

        urls = mod_json.loads(contents)

        srtm1_files = urls['srtm1']
        srtm3_files = urls['srtm3']
    except:
        srtm1_files = mod_retriever.retrieve_all_files_urls(SRTM1_URL)
        srtm3_files = mod_retriever.retrieve_all_files_urls(SRTM3_URL)

        file_handler.write(files_list_file_name,
                           mod_json.dumps({'srtm1': srtm1_files, 'srtm3': srtm3_files}, sort_keys=True, indent=4))

    assert srtm1_files
    assert srtm3_files

    return mod_data.GeoElevationData(srtm1_files, srtm3_files, file_handler=file_handler,
                                     reduce_big_files=reduce_big_files,
                                     leave_zipped=leave_zipped)

class FileHandler:
    """
    The default file handler. It can be changed if you need to save/read SRTM 
    files in a database or Amazon S3.
    """

    def get_srtm_dir(self):
        """ The default path to store files. """
        # Local cache path:
        if not mod_os.environ.has_key('HOME'):
            raise Error('No default HOME directory found, please specify a path where to store files')

        result = '{0}/.srtm'.format(mod_os.environ['HOME'])

        if not mod_path.exists(result):
            mod_os.makedirs(result)

        return result

    def exists(self, file_name):
        return mod_path.exists('%s/%s' % (self.get_srtm_dir(), file_name))

    def write(self, file_name, contents):
        with open('%s/%s' % (self.get_srtm_dir(), file_name), 'w') as f:
            f.write(contents)

    def read(self, file_name):
        with open('%s/%s' % (self.get_srtm_dir(), file_name), 'r') as f:
            return f.read()
