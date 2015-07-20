import os
import sys

from invoke import task, run


CURRENT_DIR = os.path.dirname(__file__)


@task
def setup():
    """
    Prepares to run tests.
    """
    os.chdir(CURRENT_DIR)
    print("Current directory: {}".format(os.path.dirname(__file__)))


@task(pre=[setup])
def test_all():
    """
    Runs all test sets.
    """
    test_dir = os.path.join(CURRENT_DIR, 'test')

    for dir in os.listdir(test_dir):
        if not os.path.isfile(os.path.join(test_dir, dir)) \
           and not dir.startswith('_') \
           and not dir.startswith('.'):
            test(dir)


@task(pre=[setup])
def test(name='fresh'):
    """
    Tests Mongo backup with fresh DB.
    """
    print("===== Testing '{}' set ====".format(name))
    run('test/{}/run_test.py'.format(name))
    print('')
