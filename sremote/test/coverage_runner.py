#!/usr/bin/env python
from coverage import Coverage
# I would really like to fix this stupidity, but we'll see what happens.
import sys, os
sys.path.insert(0, os.path.split(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0])[0])

from procinfo_test import ProcInfoTest
from db_test import DbTest
from app_test import ApplicationTest
from unittest import TestLoader, TextTestRunner, TestSuite

def main():
    cov = Coverage(omit=['*passlib*', '*test*'])
    cov.start()

    loader = TestLoader()
    suite = TestSuite((
        loader.loadTestsFromTestCase(ProcInfoTest),
        loader.loadTestsFromTestCase(DbTest),
        # loader.loadTestsFromTestCase(ApplicationTest),
        ))

    runner = TextTestRunner(verbosity = 2)
    runner.run(suite)

    cov.stop()
    cov.save()
    # cov.html_report()

if __name__ == '__main__':
    main()