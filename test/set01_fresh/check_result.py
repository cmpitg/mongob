#!/usr/bin/env python3

import sys
import os
sys.path.append(
    os.path.join(os.path.dirname(__file__), "../")
)

import unittest
import test_utils

from pymongo import MongoClient
from bson.json_util import loads as json_loads


def test_name():
    """
    Retrieves test name by getting current directory.
    """
    return os.path.basename(os.path.dirname(os.path.abspath(__file__)))


TEST_NAME = test_name()
TEST_INFO = test_utils.load_test_info(TEST_NAME)

##############################################################################

class TestFreshRun(unittest.TestCase):
    def test_freshrun(self):
        test_utils.print_desc('Checking result for {}'.format(TEST_NAME))

        client_src  = MongoClient(TEST_INFO['mongo_uri_src'])
        client_dest = MongoClient(TEST_INFO['mongo_uri_dest'])
        coll_src    = client_src[TEST_INFO['db_name_src']][TEST_INFO['coll_name']]
        coll_dest   = client_dest[TEST_INFO['db_name_src']][TEST_INFO['coll_name']]

        with open(TEST_INFO['dataset_file'], 'r') as input:
            data_from_file = json_loads(input.read())
            data_from_file.sort(key=lambda x: x['_id'])

        data_from_src  = list(coll_src.find().sort('_id', 1))
        data_from_dest = list(coll_dest.find().sort('_id', 1))

        self.assertEqual(data_from_file, data_from_src)
        self.assertEqual(data_from_file, data_from_dest)
    
        client_src.close()
        client_dest.close()


if __name__ == '__main__':
    unittest.main()
