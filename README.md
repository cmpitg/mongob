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

## Test sets

Note that all tests will create collections from scratch, thus **removing
existing collections with the same name in the corresponding databases** if
already existed.

### Set 01 - Fresh run

* Path: [`test/set01_fresh/`](./test/set01_fresh)

* Data set: [`test/set01_fresh/data.json`](./test/set01_fresh/data.json)

* This test sets up collection `log_traffic` in DB `adflex_test` with 101
  documents, sorted by `ObjectId`.  It then performs the backup this
  collection to `log_traffic` in DB `adflex_test_backup`.

### Set 02 - Incremental backup using `ObjectId`

* Path: [`test/set02_incremental_objectid/`](./test/set02_incremental_objectid)

* Data set:
  [`test/set02_incremental_objectid/data.json`](./test/set02_incremental_objectid/data.json)

* Progress file:
  [`test/set02_incremental_objectid/progress.json`](./test/set02_incremental_objectid/progress.json)

* This test sets up collection `log_traffic` in DB `adflex_test` with 101
  documents, sorted by `ObjectId`.  It then performs the backup 98 documents,
  starting from document with ID `555317f7d290053143db668b`, to `log_traffic`
  in DB `adflex_test_backup`.

### Set 03 - Backup all recent data in 7 days
