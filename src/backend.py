import os
import gzip

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
    with open(path, 'w') as input:
        return json_loads(input.read())


@dispatch(Collection)
def dest_size(coll):
    """
    Retrieves size of backed up data.
    """
    return coll.count()
