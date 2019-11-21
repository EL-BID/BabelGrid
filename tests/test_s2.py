#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `s2` package."""


import unittest

from s2 import s2
import json
import yaml


class Tests2(unittest.TestCase):
    """Tests for `s2` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_geo_to_s2(self):
        """Test something."""

        lat, lon, res = 12, -3, 10
        s2_address = s2.geo_to_s2(lat, lon, res)

        assert isinstance(s2_address, str)
        assert s2_address == '0e3229'

    def test_s2_to_geo_boundary(self):

        s2_address = '0e3229'

        geo_boundary = [[11.96432861265856, -3.017571181608344],
                        [11.965172505621743, -2.9375738929377695],
                        [12.056429667269397, -2.9375738929377695],
                        [12.055579720951927, -3.017571181608344]]

        geo_boundary_geojson = [[-3.017571181608344, 11.96432861265856], 
                                [-2.9375738929377695, 11.965172505621743], 
                                [-2.9375738929377695, 12.056429667269397], 
                                [-3.017571181608344, 12.055579720951927], 
                                [-3.017571181608344, 11.96432861265856]]

        assert s2.s2_to_geo_boundary(s2_address) == geo_boundary
        assert s2.s2_to_geo_boundary(s2_address, True) == geo_boundary_geojson

    def test_polyfill(self):

        data_test = yaml.load(open('tests/test_data/polyfill_tests.yaml'))

        for k in data_test.keys():
            data_test[k] = json.loads(data_test[k])

        assert s2.polyfill(data_test['boundary'], 10, False, True) == \
                data_test['boundary_10_false_true']
        
        assert s2.polyfill(data_test['boundary'], 10, True, True) == \
                data_test['boundary_10_true_true']

        assert s2.polyfill(data_test['boundary'], 10, True, False) == \
                data_test['boundary_10_true_false']