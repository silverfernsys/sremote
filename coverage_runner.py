#!/usr/bin/env python
from coverage import Coverage
from procinfo import ProcInfoTest
from db import DbTest
from unittest import TestLoader, TextTestRunner, TestSuite

def main():
    cov = Coverage()
    cov.start()

    loader = TestLoader()
    suite = TestSuite((
        loader.loadTestsFromTestCase(ProcInfoTest),
        loader.loadTestsFromTestCase(DbTest)
        ))

    runner = TextTestRunner(verbosity = 2)
    runner.run(suite)

    cov.stop()
    cov.save()
    cov.html_report()

if __name__ == '__main__':
    main()