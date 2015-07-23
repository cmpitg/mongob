from multipledispatch import dispatch

from pymongo.mongo_client import MongoClient
from io import TextIOBase


@dispatch(TextIOBase)
def close(f):
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



@dispatch(MongoClient)
def close(f):
    """
    Closes connection to MongoDB server.
    """
    f.close()
