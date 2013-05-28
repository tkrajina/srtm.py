# -*- coding: utf-8 -*-

import pdb

import logging        as mod_logging
import srtm           as mod_srtm
import srtm.retriever as mod_retriever

if __name__ == '__main__':
    mod_logging.basicConfig(level = mod_logging.DEBUG, format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

    geo_elevation_data = mod_retriever.get_geo_elevation_data()

    print 'Should be 61:', geo_elevation_data.get_elevation(46., 13.)
    print 'Should be 2700:', geo_elevation_data.get_elevation(46.999999, 13.)
    print 'Should be 1622:', geo_elevation_data.get_elevation(46.999999, 13.999999)
    print 'Should be 544:', geo_elevation_data.get_elevation(46., 13.999999)
    print 'Višnjan:', geo_elevation_data.get_elevation(45.2732, 13.7139)
    print 'Pilošćak:', geo_elevation_data.get_elevation(45.287, 13.905)
    print 'Invalid SRTM point:', geo_elevation_data.get_elevation(47.0, 13.07)
