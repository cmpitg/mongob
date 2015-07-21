# AdFlex MongoDB backup tool

## Features

* Live-adjustable backup rate.

* Incremental backup via:
  - `ObjectId`
  - Field delta, e.g. last 7 days

* Gracefully stop and resume via config file or via HTTP interface.

* Automatically read config file after each operation.

## Requirements

* Python 3
* [PyMongo](http://api.mongodb.org/python/current/) - MongoDB driver for Python
* [PyYAML](http://pyyaml.org/wiki/PyYAMLDocumentation) - YAML library for Python
* [Invoke](http://www.pyinvoke.org/) - Python-based task runner

It is recommended to use [virtualenv](https://virtualenv.pypa.io/en/latest/)
with [virtualenvwrapper](https://virtualenvwrapper.readthedocs.org/en/latest/)
in both development and deployment environment.

To install all dependencies:

```sh
pip install -r requirements.txt
```

Note that you might need to run the above command as root if you are not using
tools like virtualenv.

## Config file

## Tasks

```sh
# Run test X
invoke test --name=X

# Run all tests
invoke test_all
```

## Development guide

The `tasks.py` invoke script automatically recognizes current tests.

## Test sets

Note that all tests will create collections from scratch, thus **removing
existing collections with the same name in the corresponding databases** if
already existed.

### Set 01 - Fresh run

* Path: [`test/fresh/`](./test/fresh)

* Data set: [`test/fresh/data.json`](./test/fresh/data.json)

* Full collection backup, 101 documents.

### Set 02 - Incremental backup using `ObjectId`

* Path: [`test/incremental_objectid/`](./test/incremental_objectid)

* Data set:
  [`test/incremental_objectid/data.json`](./test/incremental_objectid/data.json)

* Progress file:
  [`test/incremental_objectid/progress.json`](./test/incremental_objectid/progress.json)

* Backup from document with `_id 555317f7d290053143db668b`, 97/101 documents.

### Set 03 - Backup all recent data in the last 7 days

* Path: [`test/last7_days/`](./test/last7_days)

* Data set:
  [`test/last7_days/data.json`](./test/last7_days/data.json)

* Generates `test_random` with 500 documents and `date` field spreading across
  last 10 days (50 documents/day).  Then backs up 350 documents in the last 7
  days.

## License

This software is distributed under the terms of the MIT license.  See
[`License`](./License) for further information.

Copyright © 2015  Ha-Duong Nguyen (@cmpitg)
