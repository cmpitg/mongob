#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../src/"))

import yaml

from pymongo import MongoClient
from bson.json_util import loads as json_loads


def load_test_info(test_name):
    """
    Loads and returns the test info YAML file and returns a Python dictionary.
    """
    test_info_path = os.path.join(
        os.path.dirname(__file__),
        test_name,
        "test_info.yaml"
    )
    with open(test_info_path, 'r') as input:
        return yaml.load(input)


# print(load_test_info('set01_fresh'))


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
