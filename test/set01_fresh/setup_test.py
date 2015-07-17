#!/usr/bin/env python3

import os

from pymongo import MongoClient
from bson.json_util import loads as json_loads

TEST_DESC       = '--- Setting up test for fresh backup ---'
MONGO_URI_SRC   = 'mongodb://localhost/'
MONGO_URI_DEST  = MONGO_URI_SRC
DB_NAME_SRC     = 'test_db'
DB_NAME_DEST    = 'test_db_backup'
COLLECTION_NAME = 'log_traffic'
DATASET_FILE    = os.path.join(os.path.dirname(__file__), 'data.json')


def main():
    print(TEST_DESC)
    client_src  = MongoClient(MONGO_URI_SRC)
    client_dest = MongoClient(MONGO_URI_DEST)
    coll_src    = client_src[DB_NAME_SRC][COLLECTION_NAME]
    coll_dest   = client_dest[DB_NAME_SRC][COLLECTION_NAME]

    print("→ Dropping {} if exists".format(COLLECTION_NAME))
    coll_src.drop()
    coll_dest.drop()

    print("→ Loading test dataset from {}".format(DATASET_FILE))
    with open(DATASET_FILE, 'r') as input:
        data = json_loads(input.read())
    coll_src.insert_many(data)

    client_src.close()
    client_dest.close()


if __name__ == '__main__':
    main()
