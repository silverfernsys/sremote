#!/usr/bin/env python
from coverage import Coverage
# I would really like to fix this stupidity, but we'll see what happens.
import sys, os
sys.path.insert(0, os.path.split(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0])[0])

def main():
    cov = Coverage(omit=[
        '*passlib*',
        '*test*',
        '*tornado*',
        '*backports_abc*',
        '*singledispatch*',
        '*six*',
        '*certifi*',
        '*daemon*',
        '*funcsigs*',
        '*mock*',
        '*pbr*',
        '*pkg_resources*',
        ])
    cov.start()

    from procinfo_test import ProcInfoTest
    from db_test import DbTest
    # from app_test import ApplicationTest
    from http_test import HTTPTestCase
    from ws_test import WebSocketTestCase
    from unittest import TestLoader, TextTestRunner, TestSuite

    loader = TestLoader()
    suite = TestSuite((
        loader.loadTestsFromTestCase(ProcInfoTest),
        loader.loadTestsFromTestCase(DbTest),
        loader.loadTestsFromTestCase(HTTPTestCase),
        loader.loadTestsFromTestCase(WebSocketTestCase),
        # loader.loadTestsFromTestCase(ApplicationTest),
        ))

    runner = TextTestRunner(verbosity = 2)
    runner.run(suite)

    cov.stop()
    cov.save()
    # cov.html_report()

if __name__ == '__main__':
    main()