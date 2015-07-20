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


TEST_NAME = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
TEST_INFO = test_utils.load_test_info(TEST_NAME)

CLIENT_SRC  = MongoClient(TEST_INFO['mongo_uri_src'])
CLIENT_DEST = MongoClient(TEST_INFO['mongo_uri_dest'])
COLL_SRC    = CLIENT_SRC[TEST_INFO['db_name_src']][TEST_INFO['coll_name']]
COLL_DEST   = CLIENT_DEST[TEST_INFO['db_name_src']][TEST_INFO['coll_name']]


##############################################################################

class TestFreshRun(unittest.TestCase):
    def test_freshrun(self):
        test_utils.print_desc('Checking result for {}'.format(TEST_NAME))

        with open(TEST_INFO['dataset_file'], 'r') as input:
            data_from_file = json_loads(input.read())
            data_from_file.sort(key=lambda x: x['_id'])

        data_from_src  = list(COLL_SRC.find().sort('_id', 1))
        data_from_dest = list(COLL_DEST.find().sort('_id', 1))

        self.assertEqual(data_from_file, data_from_src)
        self.assertEqual(data_from_file, data_from_dest)


if __name__ == '__main__':
    unittest.main()
    CLIENT_SRC.close()
    CLIENT_DEST.close()
