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

## Usage

It's probably best to explain with examples:

```sh
# Getting help
mongo_backup --help

# Running MongoBackup with config file: config.yaml, progress file:
# current_progress.yaml, and log file: mongo_backup.log
mongo_backup

# Specifying necessary files
mongo_backup --config <path-to-config.yaml> \
    --progress-file <path-to-progress.yaml> \
    --log <path-to-log>
```

Config file is automatically re-read and updated, i.e. changes to config file
take effect immediately after the currently performing operation.

After each backup operation, the program records the last document backed up
into progress file.

### Config file

Is a YAML file.  For example:

```yaml
rate: 60000
stop: false
db_source: mongodb://localhost/test_db
db_destination: mongodb://localhost/test_db_backup
collections:
  test_random:
    method: object_id
  test_random_date:
    method: date_delta
    value: -10
    unit: days
```

* `rate`: documents per second → number of documents the program tries
  backing up per second

* `stop`: flag, determines if the corresponding backup process should
  gracefully stop immediately.  `stop` is either `true` or `false`

* `db_source`:
  [MongoDB URI connection string](http://docs.mongodb.org/manual/reference/connection-string/)
  of the source database

* `db_destination`: MongoDB URI connection string of the destination database

* `collections`: an associative array with collection names as keys and backup
  methods (associative array) as values.  Currently, this program supports 2
  incremental backup methods:

  - By [ObjectId](http://docs.mongodb.org/manual/reference/object-id/),
  `method: object_id`.  Whet the program starts, it reads progress file and
  starts backing up from the document whose `ObjectId` is greater than
  `ObjectId` in the progress file.

  - By string date delta:

    ```yaml
    method: delta_date_string
    value: <value>
    unit: <date-or-time-unit>
    ```

    `unit` and `value` depend on what you have in your database.  `unit` must
    be a `YY-MM-DD` String field in the database, representing date/time.
    `value` is a number, representing the delta value, including the value.

    E.g. the following associative array makes the backup program find all
    documents in the last 10 days.

    ```Yaml
    test_random_date:
      method: date_delta
      value: -10
      unit: days
    ```

### Progress file

Is a YAML file, containing an associative array, representing ID of the last
backed up document in one collection.  E.g.

```yaml
test_random: 555317f7d290053143db668b
```

If `method` of `test_random` in config file is `object_id`, MongoBackup would
start backup all documents whose `_id` are greater than
`555317f7d290053143db668b`.

## Tasks

```sh
# Run test X
invoke test --name=X

# Run all tests
invoke test_all
```

## Development guide

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
