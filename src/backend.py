from multipledispatch import dispatch

from pymongo.mongo_client import MongoClient
from io import TextIOBase


@dispatch(TextIOBase)
def close(f):
    """
    Closes stream.
    """
    f.close()


@dispatch(MongoClient)
def close(f):
    """
    Closes connection to MongoDB server.
    """
    f.close()
