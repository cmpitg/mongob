#!/usr/bin/env python3

import sys
import os
sys.path.append(
    os.path.join(os.path.dirname(__file__), "../")
)

import yaml
import unittest

from pymongo import MongoClient
from bson.json_util import loads as json_loads
from utils import load_test_info, print_desc, print_msg, setup_dataset


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


##############################################################################

class TestFreshRun(unittest.TestCase):
    def setUp(self):
        self.test_name   = os.path.basename(CURRENT_DIR)
        self.test_info   = load_test_info(self.test_name)
        self.client_src  = MongoClient(self.test_info['mongo_src'])
        self.client_dest = MongoClient(self.test_info['mongo_dest'])
        db_src           = self.client_src[self.test_info['db_src']]
        db_dest          = self.client_dest[self.test_info['db_dest']]

        self.test_info['coll_name'] = self.get_coll_name()
        self.coll_src               = db_src[self.test_info['coll_name']]
        self.coll_dest              = db_dest[self.test_info['coll_name']]

        setup_dataset(
            uri=self.test_info['mongo_src'],
            db_name=self.test_info['db_src'],
            coll_name=self.test_info['coll_name'],
            dataset_file=os.path.join(CURRENT_DIR, 'data.json')
        )

        os.chdir(CURRENT_DIR)

    def tearDown(self):
        print_msg("Dropping {} in source and destination".format(
            self.test_info['coll_name']
        ))
        self.coll_src.drop()
        self.coll_dest.drop()

        print_msg("Removing temporary log and resource files")
        try:
            for res in self.test_info['temp_res']:
                os.remove(res)
        except Exception:
            pass

        self.client_src.close()
        self.client_dest.close()

    def test_freshrun(self):
        print_msg('Running {} test'.format(self.test_name))
        os.system(
            '../../src/mongob --config config.yaml'
            + ' --progress-file current_progress.yaml'
            + ' --log backup.log'
        )

        print_msg('Checking result for {}'.format(self.test_name))
        with open(self.test_info['dataset_file'], 'r') as input:
            data_from_file = json_loads(input.read())
            data_from_file.sort(key=lambda x: x['_id'])

        data_from_src  = list(self.coll_src.find().sort('_id', 1))
        data_from_dest = list(self.coll_dest.find().sort('_id', 1))
        
        self.assertEqual(data_from_file, data_from_src)
        self.assertEqual(data_from_file, data_from_dest)


    def get_coll_name(self):
        """
        Retrieves collection name by reading config.yaml.
        """
        with open(os.path.join(CURRENT_DIR, 'config.yaml'), 'r') as input:
            return list(yaml.load(input)['collections'].keys())[0]


if __name__ == '__main__':
    unittest.main()
