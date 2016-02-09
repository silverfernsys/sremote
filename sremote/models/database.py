# -*- coding: utf-8 -*-

import os
from datetime import datetime
import sqlite3
import time
import tablib

SQLITE_TABLES_QUERY = "SELECT * FROM sqlite_master WHERE type='table';"
SQLITE_TABLE_QUERY = "SELECT name FROM sqlite_master WHERE type='table' AND name=?;"

class ResultSet(object):
    """A set of results from a query."""
    def __init__(self, rows):
        self._rows = rows
        self._all_rows = []

    def __repr__(self):
        return '<ResultSet {:o}>'.format(id(self))

    def __iter__(self):
        '''
        Starts by returning the cached items and then consumes the
        generator in case it is not fully consumed.
        '''
        if self._all_rows:
            for row in self._all_rows:
                yield row
        try:
            while True:
                yield self.__next__()
        except StopIteration:
            pass

    def next(self):
        return self.__next__()

    def __next__(self):
        try:
            nextrow = next(self._rows)
            self._all_rows.append(nextrow)
            return nextrow
        except StopIteration:
            raise StopIteration("ResultSet contains no more rows.")

    @property
    def dataset(self):
        """A Tablib Dataset representation of the ResultSet."""
        # Create a new Tablib Dataset.
        data = tablib.Dataset()

        # Set the column names as headers on Tablib Dataset.
        data.headers = self.all()[0].keys()

        # Take each row, string-ify datetimes, insert into Tablib Dataset.
        for row in self.all():
            row = _reduce_datetimes([v for k, v in row.items()])
            data.append(row)

        return data

    def all(self):
        """Returns a list of all rows for the ResultSet. If they haven't
        been fetched yet, consume the iterator and cache the results."""

        # By calling list it calls the __iter__ method
        return list(self)


class DatabaseManager(object):
    """A Database connection manager."""
    databases = {}

    @classmethod
    def instance(self, name=None):
        try:
            if (name != None) and (name in DatabaseManager.databases):
                return DatabaseManager.databases[name]
            else:
                return DatabaseManager.databases['default']
        except Exception as e:
            raise e

    @classmethod
    def add(self, name, db_url):
        DatabaseManager.databases[name] = Database(db_url)

    @classmethod
    def remove(self, name):
        DatabaseManager.databases.pop(name, None)


class Database(object):
    """A Database connection."""

    def __init__(self, db_url=None):

        # If no db_url was provided, fallback to $DATABASE_URL.
        self.db_url = db_url

        if not self.db_url:
            raise ValueError('You must provide a db_url.')

        # Connect to the database.
        self.db = sqlite3.connect(self.db_url)
        self.db.row_factory = sqlite3.Row

    def get_table_names(self):
        """Returns a list of table names for the connected database."""
        # Return a list of tablenames.
        return [r['tbl_name'] for r in self.query(SQLITE_TABLES_QUERY)]

    def table_exists(self, tablename):
        try:
            self.query(SQLITE_TABLE_QUERY, (tablename,)).next()
            return True
        except:
            return False

    def query(self, query, params=None, fetchall=False):
        """Executes the given SQL query against the Database. Parameters
        can, optionally, be provided. Returns a ResultSet, which can be
        iterated over to get result rows as dictionaries.
        """
        # Execute the given query.
        c = self.db.cursor()
        if params:
            c.execute(query, params)
        else:
            c.execute(query)
        self.db.commit()

        # Row-by-row result generator.
        row_gen = ({k:r[k] for k in r.keys() } for r in c)
        results = ResultSet(row_gen)

        # Fetch all results if desired.
        if fetchall:
            results.all()

        return results

    def query_file(self, path, params=None, fetchall=False):
        """Like Database.query, but takes a filename to load a query from."""

        # If path doesn't exists
        if not os.path.exists(path):
        	raise FileNotFoundError

        # If it's a directory
        if os.path.isdir(path):
        	raise IsADirectoryError

        # Read the given .sql file into memory.
        with open(path) as f:
            query = f.read()

        # Defer processing to self.query method.
        return self.query(query=query, params=params, fetchall=fetchall)

def _reduce_datetimes(row):
    """Receives a row, converts datetimes to strings."""
    for i in range(len(row)):
        if isinstance(row[i], datetime):
            row[i] = '{}'.format(row[i])
    return row
