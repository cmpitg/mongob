import os
import sys

from invoke import task, run


@task
def setup():
    """
    Prepares to run tests.
    """
    os.chdir(os.path.dirname(__file__))


@task
def test_all():
    """
    Runs all test sets.
    """
    test_01()
    test_02()
    test_03()


@task(pre=[setup])
def test_01():
    """
    Tests Mongo backup with fresh DB.
    """
    print('=== Test set: Fresh backup ===')
    os.chdir('test/set01_fresh/')

    run('./setup_test.py')

    print('--- Running test ---')
    run(
        '../../src/mongo_backup.py --config config.yaml'
        + ' --progress-file current_progress.yaml'
        + ' --log backup.log'
    )

    run('./check_result.py')

    run('./teardown_test.py')
