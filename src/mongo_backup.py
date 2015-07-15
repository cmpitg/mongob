#!/usr/bin/env python3

import sys
sys.path.append(
    os.path.dirname(__file__)
)

import logging
import os
import time
import pymongo

from datetime import datetime as dt
from pymongo import MongoClient
from bson.objectid import ObjectId

from backup_logger import LOGGER


DEFAULT_CONFIG_FILE_NAME = 'config.yaml'
DEFAULT_CONFIG = {'collections': {},
                  'source_db': 'mongodb://localhost/test_db',
                  'destination_db': 'mongodb://localhost/dest_db',
                  'rate': 60000,
                  'stop': False}

CONNS      = []
LAST_TIME  = dt.now()


def create_file_if_not_exists(path, content=''):
    """
    Creates a file with a pre-defined content if not exists yet.
    """
    try:
        with open(path, 'r') as f:
            pass
    except Exception:
        with open(path, 'w') as f:
            f.write(content)


def print_collection_size(coll, logger=None):
    """
    Prints collection size.
    """
    logger = logger or LOGGER
    logger.info("{}: {} document(s)".format(coll.name, coll.count()))


def read_config(path=None):
    """
    Reads YAML config file and converts it to Python dictionary.  By default
    the file is located at DEFAULT_CONFIG_FILE_NAME.  If the config file
    doesn't exist, it is created with content DEFAULT_CONFIG.
    """
    if not path:
        path = os.path.join(
            os.path.dirname(__file__),
            DEFAULT_CONFIG_FILE_NAME
        )
    create_file_if_not_exists(
        path=path,
        content=yaml.dump(DEFAULT_CONFIG)
    )

    res = {}

    try:
        with open(path, 'r') as input:
            res = yaml.load(input)
    except Exception as e:
        sys.stderr.write(
            "Invalid YAML syntax in config.yaml: {}\n",
            str(e)
        )
        sys.exit(1)

    check_stop_flag(res)

    return res


def check_stop_flag(config):
    """
    Checks if the stop flag presents in config and stop the application
    gracefully if it is.
    """
    if not config.get('stop', False):
        return

    for conn in CONNS:
        conn.close()

    print("Stopped by user.")

    sys.exit(0)


def report_collections_size(db, coll_names, logger=None):
    """
    Reports size of all collections.
    """
    logger = logger or LOGGER

    logger.info("all collection size:")

    for name in coll_names:
        print_collection_size(
            db[name],
            logger=logger
        )


def milisecs_passed(last_time=None):
    """
    Calculates time passed since last_time in miliseconds.
    """
    last_time = last_time or LAST_TIME
    delta = int((dt.now() - LAST_TIME).total_seconds() * 1000)
    return delta


def balance_rate(unit=None, last_time=None):
    """
    Sleeps if necessary to keep up with current backup rates and updates
    current execution time to LAST_TIME.
    """
    global LAST_TIME
    last_time = last_time or LAST_TIME
    unit      = unit or 1000

    delta = milisecs_passed()
    if delta < unit:
        time.sleep((unit - delta) / 1000)
        LAST_TIME = dt.now()


# LAST_TIME = dt.now(); balance_rate(); milisecs_passed()


def build_query(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            res = f.read()
        return { "_id": { "$gt": ObjectId(res) }}
    else:
        return {}


def backup_collection(name):
    global LAST_TIME

    LOGGER.info("processing collection %s", name)
    LOGGER.info("source: %s; destination: %s",
                         SOURCE_DB[name].count(),
                         DEST_DB[name].count())
    LAST_TIME = dt.now()

    source_collection = SOURCE_DB[name]
    dest_collection   = DEST_DB[name]
    current_docs      = []
    config            = read_config()
    # docs              = source_collection.find().sort([('_id', pymongo.DESCENDING )])
    docs              = source_collection.find().sort([('date', pymongo.DESCENDING )]).limit(MAX_DOCUMENTS)

    def insert_to_dest():
        LOGGER.info('rate: %s → batch inserting %s documents into %s',
                             config['rate'],
                             len(current_docs),
                             name)
        dest_collection.insert_many(current_docs)
        sleep_if_necessary()

    def doc_exists(doc, coll):
        return len(list(coll.find({ u'_id': doc[u'_id'] }))) != 0

    for doc in docs:
        if doc_exists(doc=doc, coll=dest_collection):
            continue
            # break

        current_docs.append(doc)

        if len(current_docs) >= config['rate']:
            insert_to_dest()
            config = read_config()
            current_docs = []

    if len(current_docs) != 0:
        insert_to_dest()
        config = read_config()
        current_docs = []


def init():
    milisecs_passed()


def backup():
    init()
    for name in COLLECTIONS:
        backup_collection(name)


def main():
    # report_collections_size()
    backup()

    SOURCE.close()
    DEST.close()


if __name__ == '__main__':
    main()
