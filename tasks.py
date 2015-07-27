#
# Copyright © 2015  Ha-Duong Nguyen <NOTcmpitgATgmailDOTcom>
#
# This file is distributed under the terms of the MIT license.
#

import os
import sys

from invoke import task, run


CURRENT_DIR = os.path.dirname(__file__)
TESTS_DIR   = os.path.join(CURRENT_DIR, 'tests')


@task
def setup():
    """
    Prepares to run tests.
    """
    os.chdir(CURRENT_DIR)
    # print("Current directory: {}".format(os.path.dirname(__file__)))


@task(pre=[setup])
def test_all():
    """
    Runs all test sets.
    """
    for name in test_names():
        test(name=name)


@task(pre=[setup])
def test(name='fresh'):
    """
    Tests Mongo backup with fresh DB.
    """
    print("===== Testing '{}' set =====".format(name))
    run('{}/{}/run_test.py'.format(TESTS_DIR, name))
    print('')


@task(pre=[setup])
def list_test():
    """
    Displays all test names.
    """
    for name in test_names():
        print(name)


def test_names():
    """
    Retrieves all test names.
    """
    return [dir for dir in os.listdir(TESTS_DIR)
            if not os.path.isfile(os.path.join(TESTS_DIR, dir)) \
            and not dir.startswith('_') \
            and not dir.startswith('.')]
