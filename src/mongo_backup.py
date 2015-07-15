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
from datetime import timedelta
from pymongo import MongoClient
from bson.objectid import ObjectId

from backup_logger import LOGGER


DEFAULT_CONFIG_FILE_NAME = os.path.join(
    os.path.dirname(__file__),
    'config.yaml'
)
DEFAULT_PROGRESS_FILE    = os.path.join(
    os.path.dirname(__file__),
    'current_progress.yaml'
)

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
    path = path or DEFAULT_CONFIG_FILE_NAME
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


def update_last_time(new_value=None):
    """
    Updates `LAST_TIME'.
    """
    global LAST_TIME
    LAST_TIME = new_value or dt.now()


def balance_rate(unit=None, last_time=None):
    """
    Sleeps if necessary to keep up with current backup rates and updates
    current execution time to LAST_TIME.
    """
    last_time = last_time or LAST_TIME
    unit      = unit or 1000

    delta = milisecs_passed()
    if delta < unit:
        time.sleep((unit - delta) / 1000)
        update_last_time()


# LAST_TIME = dt.now(); balance_rate(); milisecs_passed()


def build_query(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            res = f.read()
        return { "_id": { "$gt": ObjectId(res) }}
    else:
        return {}


def find_docs_to_update(coll,
                        condition=None,
                        progress_path=None,
                        logger=None
):
    """
    Builds and queries list of docs to update in `coll'.  If `condition' is
    None or not supplied, find all documents.  TODO: documentation about
    grammar that `condition' supports.
    """
    if not condition or condition == [] or condition == {}:
        return coll.find()

    logger        = logger or LOGGER
    progress_path = progress_path or DEFAULT_PROGRESS_FILE
    method        = condition['method']
    name          = coll.name

    create_file_if_not_exists(progress_path, yaml.dump({}))

    if method == 'object_id':
        # Find all documents having IDs greater than the saved Object ID
        with open(progress_path, 'r') as input:
            start_id = yaml.load(input).get(name, '')

        if start_id == '':
            return coll.find()
        else:
            logger.info('starting from ObjectId: %s', start_id)
            return coll.find({ "_id": { "$gt": ObjectId(start_id) }})

    elif method == 'date_delta':
        # Find all documents having 'date' field ≥ now() - delta
        delta = timedelta(**{ condition['unit']: condition['value']})
        start_date = (dt.now().date() - delta).strftime('%Y-%m-%d')

        logger.info('starting from date: %s', start_date)
        return coll.find({ 'date': { "$gte": start_date } })
        

# adb = MongoClient('mongodb://localhost/)
# find_docs_to_update(adb.log_traffic).count()
# log_last_doc('log_traffic', '555317f7d290053143db66b2')
# find_docs_to_update(adb.log_traffic, { 'method': 'object_id' }).count()
# => 58
# log_last_doc('log_traffic', '555317f7d290053143db668a')
# find_docs_to_update(adb.log_traffic, { 'method': 'object_id' }).count()
# => 98


def log_last_doc(coll_name, doc_id, logger=None, path=None):
    """
    Logs last document inserted into `path' as YAML.
    """
    logger  = logger or LOGGER
    path    = path or DEFAULT_PROGRESS_FILE

    create_file_if_not_exists(path=path, content=yaml.dump({}))

    with open(path, 'r') as input:
        progress = yaml.load(input)

    progress[coll_name] = doc_id

    with open(path, 'w') as output:
        output.write(yaml.dump(progress))

    logger.info('last document ID: %s in %s', doc_id, coll_name)


def backup_collection(coll_src,
                      coll_dest,
                      condition=None,
                      config_path=None,
                      logger=None):
    """
    Backups collection from coll_src to coll_dest with a pre-defined search
    condition.
    """
    logger        = logger or LOGGER
    current_docs  = []
    config        = read_config(path=config_path)
    docs          = find_docs_to_update(coll_src, condition)

    logger.info(
        "backing up %s (%s docs) ⇒ %s (%s docs)",
        coll_src.name,
        coll_src.count(),
        coll_dest.name,
        coll_dest.count()
    )
    logger.info('rate: %s doc(s)/sec', config['rate'])

    update_last_time()

    def insert_to_dest():
        nonlocal config
        nonlocal current_docs

        logger.info(
            'bulk inserting: %s → %s',
            len(current_docs),
            coll_dest.name
        )

        try:
            coll_dest.insert_many(current_docs, ordered=False)
        except Exception as e:
            passed

        log_last_doc(
            coll_name=coll_dest.name,
            doc=current_docs[-1]
        )

        balance_rate()
        config       = read_config()
        current_docs = []

    for doc in docs:
        current_docs.append(doc)
        if len(current_docs) >= config['rate']:
            insert_to_dest()

    if len(current_docs) != 0:
        insert_to_dest()


# adb = MongoClient('mongodb://localhost/)
# backup_collection(adb.log_traffic, adb.log_traffic_2, config_path='/m/src/adflex/db_backup/src/config.yaml')


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

# try:
#     aa.insert_many([{ '_id': doc1 }, { '_id': doc2 }, { '_id': doc3 }], ordered=False)
# except Exception as e:
#     print(str(e))
