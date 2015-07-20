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

## Test sets

Note that all tests will create collections from scratch, thus **removing
existing collections with the same name in the corresponding databases** if
already existed.

### Set 01 - Fresh run

* Path: [`test/fresh/`](./test/fresh)

* Data set: [`test/fresh/data.json`](./test/fresh/data.json)

* This test sets up collection `test_random` with 101 documents, sorted by
  `ObjectId`.  It then performs the backup this collection and checks if the
  destination documents are the same as their source counterparts.

### Set 02 - Incremental backup using `ObjectId`

* Path: [`test/incremental_objectid/`](./test/incremental_objectid)

* Data set:
  [`test/incremental_objectid/data.json`](./test/incremental_objectid/data.json)

* Progress file:
  [`test/incremental_objectid/progress.json`](./test/incremental_objectid/progress.json)

* This test sets up collection `test_random` with 101 documents, sorted by
  `ObjectId`.  It then performs the backup 98 documents, starting from
  document with ID `555317f7d290053143db668b` and checks if the result is
  correct.

### Set 03 - Backup all recent data in the last 7 days

* Path: [`test/last7_days/`](./test/last7_days)

* Data set:
  [`test/last7_days/data.json`](./test/last7_days/data.json)

* This test generates collection `test_random` consisting of 500 documents
  with `date` field spreading across 10 days (50 documents/day).  It then
  performs the backup 350 documents in the last 7 days to `test_random` and
  checks if the result is correct.

## License

This software is distributed under the terms of the MIT license.  See
[`License`](./License) for further information.

Copyright © 2015  Ha-Duong Nguyen (@cmpitg)
