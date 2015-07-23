import os
import bz2
import sys

from multipledispatch import dispatch
from bson.json_util import loads as json_loads
from bson.json_util import dumps as json_dumps

from pymongo.mongo_client import MongoClient
from pymongo.database     import Database
from pymongo.collection   import Collection
from io import TextIOBase


##############################################################################

def get_db(uri, connections):
    """
    Retrieves database from connection string.  The connection string
    follows one of the formats:
    'mongodb://[username][[:[password]]@]<host>/<db_name>'
    or 'file://<path>'
    or simply '<path>'.
    """

    if uri.startswith('mongodb://'):
        db_name_pos = uri.rfind("/") + 1
        client      = MongoClient(uri[:db_name_pos])
        db          = client[uri[db_name_pos:]]
    else:
        if uri.startswith("file://"):
            uri = uri[len("file://"):]
        client      = uri
        db          = uri

    try:
        connections.index(client)
    except Exception:
        connections.append(client)

    return connections, db


# print(get_db("mongodb://localhost/hello_world", []))
# print(get_db("file:///tmp/hello_world.txt",     []))
# print(get_db("/tmp/hi_hi.txt",                  []))


##############################################################################

@dispatch(str, str)
def get_collection(db, name):
    """
    Retrieves collection from a MongoDB database.
    """
    return db


@dispatch(Database, str)
def get_collection(db, name):
    """
    Retrieves collection from a MongoDB database.
    """
    return db[name]


##############################################################################

@dispatch(str)
def close(path):
    pass


@dispatch(MongoClient)
def close(client):
    """
    Closes connection to MongoDB server.
    """
    client.close()


##############################################################################

@dispatch(str)
def dest_name(path):
    """
    Retrieves name of destination collection.
    """
    return os.path.basename(path)


@dispatch(Collection)
def dest_name(coll):
    """
    Retrieves name of destination file.
    """
    return coll.name


##############################################################################

@dispatch(str)
def dest_size(path):
    """
    Retrieves size of backed up data.
    """
    try:
        with bz2.open(path, 'rt') as input:
            return json_loads(input.read())
    except Exception:
        return 0


@dispatch(Collection)
def dest_size(coll):
    """
    Retrieves size of backed up data.
    """
    return coll.count()

##############################################################################

@dispatch(str, list)
def insert_docs(path, docs):
    """
    Inserts all docs into a destination file.  This function makes no attempt
    at making sure there are no duplicated docs.
    """
    # Not used:
    # As we write one list each time we open destination while the desire output
    # should be a single list, we need to do the list concatenation manually by
    # removing the closing square bracket ("]") and add a comma to separate the
    # currently inserted items.

    # Destination file is created for the first time
    if not os.path.isfile(path):
        with bz2.open(path, 'wt') as output:
            output.write(json_dumps(docs))
    else:
        # with bz2.open(path, 'r') as output:
        #     # Remove last ]
        #     output.seek(-1, os.SEEK_END)
        #     while output.peek(1)[:1] != b']' and output.tell() > 0:
        #         print(output.peek(1)[:1])
        #         output.seek(-1, os.SEEK_CUR)
        #     output.truncate()

        #     # Write , as list separator
        #     output.write(b', ')

        #     # Now, write docs without the beginning [
        #     output.write(json_dumps(docs)[1:].encode('utf-8'))

        with bz2.open(path, 'rt') as input:
            current_docs = json_loads(input.read())
        current_docs.extend(docs)

        with bz2.open(path, 'wt') as output:
            output.write(json_dumps(current_docs))


@dispatch(Collection, list)
def insert_docs(coll, docs):
    """
    Inserts all docs into a MongoDB collection.
    """
    coll.insert_many(docs, ordered=False)
