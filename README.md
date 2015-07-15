# AdFlex MongoDB backup tool

## Features

* Live-adjustable backup rate.

* Incremental backup via:
  - `ObjectId`$$$
  - Field range, e.g. `date` between 2 values.

* Gracefully stop and resume via config file or via HTTP interface.

* Automatically read config file after each operation.

## Requirements

* Python 3
* [PyMongo](http://api.mongodb.org/python/current/)
* [PyYAML](http://pyyaml.org/wiki/PyYAMLDocumentation)

It is recommended to use [virtualenv](https://virtualenv.pypa.io/en/latest/)
with [virtualenvwrapper](https://virtualenvwrapper.readthedocs.org/en/latest/)
in both development and deployment environment.  After that, dependecies can
be easily installed with:

```sh
pip install pymongo PyYAML
```

## Config file
