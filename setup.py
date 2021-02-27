#!/usr/bin/python
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

import distutils.core as mod_distutilscore

mod_distutilscore.setup(
    name = 'SRTM.py',
    version = '0.3.7',
    description = 'Python parser for the Shuttle Radar Topography Mission elevation data',
    license = 'Apache License, Version 2.0',
    author = 'Tomo Krajina',
    author_email = 'tkrajina@gmail.com',
    url = 'https://github.com/tkrajina/srtm.py',
    packages = ['srtm',],
    package_data = {'': ['*.json']},
    include_package_data = True,
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    install_requires=['requests'],
    scripts=['gpxelevations']
)

