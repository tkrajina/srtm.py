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

import logging    as mod_logging
import math       as mod_math
import zipfile    as mod_zipfile
import pathlib    as mod_pathlib
import os         as mod_os
import os.path    as mod_path

from io import BytesIO as cStringIO # looks hacky but we are working with bytes
from typing import *

ONE_DEGREE = 1000. * 10000.8 / 90.

DEFAULT_TIMEOUT = 15

class Color(NamedTuple):
    red: int
    green: int
    blue: int
    alpha: int

def distance(latitude_1: float, longitude_1: float, latitude_2: float, longitude_2: float) -> float:
    """
    Distance between two points.
    """
    coef = mod_math.cos(latitude_1 / 180. * mod_math.pi)
    x = latitude_1 - latitude_2
    y = (longitude_1 - longitude_2) * coef

    return mod_math.sqrt(x * x + y * y) * ONE_DEGREE

def get_color_between(color1: Color, color2: Color, i: float) -> Color:
    """ i is a number between 0 and 1, if 0 then color1, if 1 color2, ... """
    if i <= 0:
        return color1
    if i >= 1:
        return color2
    return Color(int(color1[0] + (color2[0] - color1[0]) * i),
            int(color1[1] + (color2[1] - color1[1]) * i),
            int(color1[2] + (color2[2] - color1[2]) * i),
            int(color1[3] + (color2[3] - color1[3]) * i))

def zip(contents: bytes, file_name: str) -> bytes:
    mod_logging.debug('Zipping %s bytes' % len(contents))
    result = cStringIO()
    zip_file = mod_zipfile.ZipFile(result, 'w', mod_zipfile.ZIP_DEFLATED, False)
    zip_file.writestr(file_name, contents)
    zip_file.close()
    result.seek(0)
    mod_logging.debug('Zipped')
    return result.read()

def unzip(contents: bytes) -> bytes:
    mod_logging.debug('Unzipping %s bytes' % len(contents))
    zip_file = mod_zipfile.ZipFile(cStringIO(contents))
    zip_info_list = zip_file.infolist()
    for zi in zip_info_list:
        if zi.filename[0] != ".":
            result = zip_file.open(zi).read()
            mod_logging.debug('Unzipped')
            return result
    raise Exception(f"No valid file found in {zip_info_list}")

class FileHandler:
    """
    The default file handler. It can be changed if you need to save/read SRTM
    files in a database or Amazon S3.
    """

    def __init__(self, local_cache_dir: Optional[str]=None) -> None:
        if local_cache_dir:
            self.local_cache_dir = local_cache_dir
        else:
            home_dir = str(mod_pathlib.Path.home()) or mod_os.environ.get("HOME") or mod_os.environ.get("HOMEPATH") or ""
            if not home_dir:
                raise Exception('No default HOME directory found')
            self.local_cache_dir = mod_os.sep.join([home_dir, '.cache', 'srtm'])

        if not mod_path.exists(self.local_cache_dir):
            print(f"Creating {self.local_cache_dir}")
            try:
                mod_os.makedirs(self.local_cache_dir)
            except Exception as e:
                print(f"Local cache dir: {self.local_cache_dir}")
                raise Exception(f"Error creating directory {self.local_cache_dir}: {e}")

    def exists(self, file_name: str) -> bool:
        return mod_path.exists(mod_os.path.join(self.local_cache_dir, file_name))

    def write(self, file_name: str, contents: bytes) -> None:
        print(4, len(contents))
        fn = mod_os.path.join(self.local_cache_dir, file_name)
        with open(fn, 'wb') as f:
            n = f.write(contents)
            mod_logging.debug(f"saved {n} bytes in {fn}")

    def read(self, file_name: str) -> bytes:
        with open(mod_os.path.join(self.local_cache_dir, file_name), 'rb') as f:
            return f.read()