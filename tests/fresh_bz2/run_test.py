#!/usr/bin/env python3

import sys
import os
sys.path.append(
    os.path.join(os.path.dirname(__file__), "../")
)

import yaml
import unittest
import bz2

from pymongo        import MongoClient
from bson.json_util import loads as json_loads

from utils import load_test_info
from utils import print_desc
from utils import print_msg
from utils import setup_dataset
from utils import remove_res


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


##############################################################################

class TestFreshRun(unittest.TestCase):
    def setUp(self):
        os.chdir(CURRENT_DIR)

        self.test_name   = os.path.basename(CURRENT_DIR)
        self.test_info   = load_test_info(self.test_name)

        self.coll_name   = self.test_info['coll_names'][0]

        self.conn_src    = self.test_info['conn_src']
        self.db_src      = self.test_info['db_src']
        self.db_dest     = self.test_info['db_dest']
        self.coll_src    = self.db_src[self.coll_name]

        remove_res(self.test_info['temp_res'])

        setup_dataset(
            coll=self.coll_src,
            dataset_file=os.path.join(CURRENT_DIR, 'data.json')
        ) 

    def tearDown(self):
        print_msg("Dropping {} in source".format(
            self.coll_name
        ))
        self.coll_src.drop()
        self.conn_src.close()

        # remove_res(self.test_info['temp_res'])

    def test_freshbz2(self):
        print_msg('Running {} test'.format(self.test_name))
        os.system(
            '../../src/mongob --config config.yaml'
            + ' --progress-file current_progress.yaml'
            + ' --log backup.log'
        )

        print_msg('Checking result for {}'.format(self.test_name))
        with open(self.test_info['dataset_file'], 'rt') as input:
            data_from_file = json_loads(input.read())
            data_from_file.sort(key=lambda x: x['_id'])

        data_from_src  = list(self.coll_src.find().sort('_id', 1))

        with bz2.open(self.db_dest, 'rt') as input:
            data_from_dest = json_loads(input.read())
        data_from_dest.sort(key=lambda x: x['_id'])
        
        self.assertEqual(data_from_file, data_from_src)
        self.assertEqual(data_from_file, data_from_dest)


if __name__ == '__main__':
    unittest.main()
