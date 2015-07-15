# AdFlex MongoDB backup tool

## Features

* Live-adjustable backup rate.

* Incremental backup via:
  - `ObjectId`$$$
  - Field range, e.g. `date` between 2 values.

* Gracefully stop and resume via config file or via HTTP interface.

* Automatically read config file after each operation.

## Config file
