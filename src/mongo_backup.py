#!/usr/bin/env python3

import logging
import sys
import os
import time
import pymongo

from datetime import datetime as dt
from pymongo import MongoClient
from bson.objectid import ObjectId


log_formatter              = logging.Formatter('%(asctime)s : %(message)s')
log_progress_file_handler  = logging.FileHandler('mongo_backup_progress.log',
                                                mode='a+')
log_progress_file_handler.setFormatter(log_formatter)
log_stream_handler = logging.StreamHandler()
log_stream_handler.setFormatter(log_formatter)
LOGGER_PROGRESS = logging.getLogger('progress')
LOGGER_PROGRESS.setLevel(logging.INFO)
LOGGER_PROGRESS.addHandler(log_progress_file_handler)
LOGGER_PROGRESS.addHandler(log_stream_handler)

SOURCE         = MongoClient("mongodb://adsinapp:aDsinApP123@125.212.201.147/ads_in_app")
SOURCE_DB      = SOURCE.ads_in_app
DEST           = MongoClient("mongodb://adsinapp:aDsinApP123@125.212.201.146/ads_in_app")
DEST_DB        = DEST.ads_in_app
MAX_DOCUMENTS  = 500000

LAST_TIME        = dt.now()
TOTAL_DOCUMENTS  = 0



def create_file_if_not_exists(path):
    try:
        with open(path, 'r') as f:
            pass
    except Exception:
        with open(path, 'w') as f:
            pass


def print_collection_size(name):
    """Print collection size"""
    coll = SOURCE_DB[name]
    print("{}: {}".format(name, coll.count()))


def read_config(path=None):
    try:
        if not path:
            path = os.path.join(os.path.dirname(__file__), "rate.txt")

        with open(path, 'r') as inp:
            lines = inp.readlines()

        if len(lines) > 1 and str.startswith(lines[1], 'stop'):
            LOGGER_PROGRESS.warn('stopped by user')
            sys.exit(1)
            
        else:
            return {
                'rate': int(lines[0]),
                'stop': False
            }
    except Exception as e:
        print(str(e))
        return {
            'rate': 1000,
            'stop': False
        }


def report_collections_size():
    LOGGER_PROGRESS.info("collections with MongoID")
    map(print_collection_size, COLLECTIONS)

    # LOGGER_PROGRESS.info("collections without MongoID")
    # map(print_collection_size, COLLECTIONS_DATE)


def milisecs_passed():
    delta = int((dt.now() - LAST_TIME).total_seconds() * 1000)
    return delta


def sleep_if_necessary():
    global LAST_TIME

    delta = milisecs_passed()
    if delta < 1000:
        time.sleep((1000 - delta) / 1000)
        LAST_TIME = dt.now()


def build_query(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            res = f.read()
        return { "_id": { "$gt": ObjectId(res) }}
    else:
        return {}


def backup_collection(name):
    global LAST_TIME

    LOGGER_PROGRESS.info("processing collection %s", name)
    LOGGER_PROGRESS.info("source: %s; destination: %s",
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
        LOGGER_PROGRESS.info('rate: %s → batch inserting %s documents into %s',
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
