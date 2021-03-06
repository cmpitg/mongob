# Mongob - collection-to-collection backup tool for MongoDB

## Features

* Adjustable backup rate.

* Supports MongoDB instance or Bz2-compressed file as backup destination.

* Config file takes effect immediately.

* Incremental backup via:
  - `ObjectId`
  - Date-string delta, e.g. last 7 days

* Gracefully stop and resume via config file.

Mongob is currently used in production by [Eway](http://eway.vn/)'s
[AdFlex](http://adflex.vn/) as a regular MongoDB backup tool.

## Requirements

* Python 3
* [PyMongo](http://api.mongodb.org/python/current/) - MongoDB driver for Python
* [PyYAML](http://pyyaml.org/wiki/PyYAMLDocumentation) - YAML library for Python
* [Invoke](http://www.pyinvoke.org/) - Python-based task runner
* [multipledispatch](https://github.com/mrocklin/multipledispatch/) - Multiple
  dispatch for Python

It is recommended to use [virtualenv](https://virtualenv.pypa.io/en/latest/)
with [virtualenvwrapper](https://virtualenvwrapper.readthedocs.org/en/latest/)
in both development and deployment environments.

To install all dependencies:

```sh
pip install -r requirements.txt
```

Note that you might need to run the above command as root if you are not using
virtualenv.

## Usage

```sh
# Getting help
mongo_backup --help

# Running Mongob with config file: config.yaml, progress file:
# current_progress.yaml, and log file: mongo_backup.log
mongob

# Specifying necessary files
mongob --config <path-to-config.yaml> \
    --progress-file <path-to-progress.yaml> \
    --log <path-to-log>
```

Changes to config file take effect immediately after current operation.

After each backup operation, Mongob records the last backed-up document into
progress file.

### Config file

YAML format.  E.g.

```yaml
rate: 60000
stop: false
db_source: mongodb://localhost/test_db
db_destination: mongodb://localhost/test_db_backup
collections:
  test_random:
    method: object_id
    remove_after_backup: false
  test_random_date:
    method: date_delta
    value: -10
    unit: days
```

* `rate`: documents per second

* `stop`: flag, determines if the corresponding backup process should
  gracefully stop immediately.  `stop` is either `true` or `false`.

* `db_source`:
  [MongoDB URI connection string](http://docs.mongodb.org/manual/reference/connection-string/)
  of the source database

* `db_destination`: Either a MongoDB URI connection string of the destination
  database (`mongodb://`) or path to the backup file (`file://` or no
  protocol).  In the latter case, the backup is a Bz2-compressed JSON file.
  Currently it is **not** recommended to use Bz2-compressed file as backup
  destination as it might be really slow.

* `collections`: an associative array with collection names as keys and backup
  methods as values.  Currently, this program supports 2 incremental backup
  methods:

  - By [ObjectId](http://docs.mongodb.org/manual/reference/object-id/),
  `method: object_id`.  When Mongob starts, it reads the progress file and
  starts backing up from the document whose `ObjectId` is greater than
  `ObjectId` in the progress file.

  - By string date delta:

    ```yaml
    method: delta_date_string
    value: <value>
    unit: <date-or-time-unit>
    ```

    `unit` and `value` depend on what you have in your database.  `unit` must
    be a `YYYY-MM-DD` String field, representing date/time.  `value` is a
    number, representing the delta value, including the value.

    E.g. to backup all documents in `test_random_date` in the last 10 days:

    ```Yaml
    test_random_date:
      method: date_delta
      value: -10
      unit: days
    ```

* `remove_after_backup` determines whether or not the newly backed up
  documents are removed from the source collection.  By default,
  `remove_after_backup` is `false` if not exists.

### Progress file

YAML format, containing an associative array representing `_id` of the last
backed up document in one collection.  E.g.

```yaml
test_random: 555317f7d290053143db668b
```

If `method` of `test_random` in config file is `object_id`, Mongob would
backup all documents whose `_id` are greater than `555317f7d290053143db668b`.
Otherwise, this file has no effect on the backup process.

## Development notes

Should you find any problems or have suggestion, please don't hesitate to
contact me via
[Github issue tracker](https://github.com/cmpitg/mongob/issues).

### Tasks

```sh
# List all tasks
invoke -l
# or
invoke --list

# List all test names
invoke list_test

# Run test X
invoke test --name=X

# Run all tests
invoke test_all
```

### Tests

Note that all tests will create collections from scratch, thus **removing
existing collections with the same name in the corresponding databases** if
they have already existed.

### Fresh run

* Path: [`tests/fresh/`](./tests/fresh)

* Data set: [`tests/fresh/data.json`](./tests/fresh/data.json)

* Full collection backup, 101 documents.

### Fresh run Bz2

* Path: [`tests/fresh_bz2/`](./tests/fresh_bz2)

* Data set: [`tests/fresh_bz2/data.json`](./tests/fresh_bz2/data.json)

* Full collection backup, 101 documents, Bz2-compressed file as backup
  destination.

### Fresh run with `remove_after_backup`

* Path: [`tests/fresh_remove_after_backup/`](./tests/fresh_remove_after_backup)

* Data set:
  [`tests/fresh_remove_after_backup/data.json`](./tests/fresh_remove_after_backup/data.json)

* Full collection backup, 101 documents, documents are removed after backup
  completes.

### Incremental backup using `ObjectId`

* Path: [`tests/incremental_objectid/`](./tests/incremental_objectid)

* Data:
  [`tests/incremental_objectid/data.json`](./tests/incremental_objectid/data.json)

* Progress file:
  [`tests/incremental_objectid/progress.json`](./tests/incremental_objectid/progress.json)

* Backup all documents with `_id ≥ ObjectId(555317f7d290053143db668b)`, 97/101
  documents.

### Backup all data in the last 7 days

**TODO**

* Path: [`tests/last7_days/`](./tests/last7_days)

* Data set:
  [`tests/last7_days/data.json`](./tests/last7_days/data.json)

* Generates `test_random` with 500 documents and `date` field spreading across
  last 10 days (50 documents/day).  Then performs backup 350 documents in the
  last 7 days.

## License

This software is distributed under the terms of the MIT license.  See
[`License`](./License) for further information.

Copyright © 2015  Ha-Duong Nguyen (@cmpitg)
