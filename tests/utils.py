#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

import yaml

from pymongo import MongoClient
from bson.json_util import loads as json_loads


CURRENT_DIR = os.path.dirname(__file__)


def parse_mongo_uri(uri):
    """
    Parses and returns MongoDB origin and its corresponding DB.  If the URI
    indicates a file, return the path to the file as both values.
    """
    if uri.startswith('mongodb://'):
        db_name_pos = uri.rfind("/") + 1
        db_name     = uri[db_name_pos:]
        mongo_src   = uri[:db_name_pos]
        return mongo_src, db_name
    else:
        return uri, uri


def load_test_info(test_name):
    """
    Loads and returns the test info YAML file and returns a Python dictionary.
    """
    test_info_path  = os.path.join(CURRENT_DIR, test_name, "test_info.yaml")
    config_path     = os.path.join(CURRENT_DIR, test_name, "config.yaml")

    with open(test_info_path, 'r') as input:
        test_info = yaml.load(input)
    with open(config_path, 'r') as input:
        config    = yaml.load(input)

    test_info['mongo_src'], test_info['db_src'] = parse_mongo_uri(
        config['db_source']
    )
    test_info['mongo_dest'], test_info['db_dest'] = parse_mongo_uri(
        config['db_destination']
    )

    return test_info

# print(load_test_info('fresh'))


def print_desc(desc):
    """
    Prints the test description.
    """
    sys.stdout.write("--- {} ---\n".format(desc))
    sys.stdout.flush()


def print_msg(msg):
    """
    Prints a test message.
    """
    sys.stdout.write("→ {}\n".format(msg))
    sys.stdout.flush()


def setup_dataset(uri, db_name, coll_name, dataset_file):
    """
    Setting up data set for a test by dropping the existing collection then
    loading data from a JSON file.
    """
    print_msg("Loading dataset for {}".format(coll_name))

    with MongoClient(uri) as client:
        db     = client[db_name]
        coll   = db[coll_name]
        coll.drop()

        with open(dataset_file, 'r') as input:
            coll.insert_many(json_loads(input.read()))
