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
        '*tablib*',
        ])

    cov.start()
    
    from app_test import ApplicationTest
    from database_test import DatabaseTest
    from db_test import DbTest
    from http_test import HTTPTestCase
    from procinfo_test import ProcInfoTest
    from user_test import UserTest
    from token_test import TokenTest
    from ws_test import WebSocketTestCase
    from unittest import TestLoader, TextTestRunner, TestSuite

    loader = TestLoader()
    suite = TestSuite((
        loader.loadTestsFromTestCase(ProcInfoTest),
        loader.loadTestsFromTestCase(DbTest),
        loader.loadTestsFromTestCase(DatabaseTest),
        loader.loadTestsFromTestCase(UserTest),
        loader.loadTestsFromTestCase(TokenTest),
        loader.loadTestsFromTestCase(HTTPTestCase),
        loader.loadTestsFromTestCase(WebSocketTestCase),
        loader.loadTestsFromTestCase(ApplicationTest),
        ))

    runner = TextTestRunner(verbosity = 2)
    runner.run(suite)

    cov.stop()
    cov.save()
    # cov.html_report()

if __name__ == '__main__':
    main()