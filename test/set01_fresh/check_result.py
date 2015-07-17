#!/usr/bin/env python3

import os
import unittest

from pymongo import MongoClient
from bson.json_util import loads as json_loads

TEST_DESC       = '--- Checking result ---'
MONGO_URI_SRC   = 'mongodb://localhost/'
MONGO_URI_DEST  = MONGO_URI_SRC
DB_NAME_SRC     = 'test_db'
DB_NAME_DEST    = 'test_db_backup'
COLLECTION_NAME = 'log_traffic'
DATASET_FILE    = os.path.join(os.path.dirname(__file__), 'data.json')


class TestFreshRun(unittest.TestCase):
    def test_freshrun(self):
        print(TEST_DESC)
        client_src  = MongoClient(MONGO_URI_SRC)
        client_dest = MongoClient(MONGO_URI_DEST)
        coll_src    = client_src[DB_NAME_SRC][COLLECTION_NAME]
        coll_dest   = client_dest[DB_NAME_SRC][COLLECTION_NAME]

        with open(DATASET_FILE, 'r') as input:
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
