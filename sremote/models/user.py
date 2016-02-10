# -*- coding: utf-8 -*-
import time
from passlib.apps import custom_app_context as pwd_context
from model import Manager, Model
from database import Database, DatabaseManager

class UserManager(Manager):
    CREATE_TABLE_QUERY = """CREATE TABLE user (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                username TEXT, password TEXT, admin INTEGER, created TIMESTAMP, UNIQUE(username));"""
    DROP_TABLE_QUERY = """DROP TABLE user;"""
    CREATE_OBJECT_QUERY = """INSERT INTO user VALUES (?,?,?,?,?);"""
    DELETE_OBJECT_QUERY = """DELETE FROM user WHERE id=?;"""
    UPDATE_OBJECT_QUERY = 'UPDATE user SET username=?, password=?, admin=? WHERE id=?;'
    GET_OBJECT_QUERY = 'SELECT * FROM user WHERE username=?;'
    COUNT_OBJECT_QUERY = 'SELECT COUNT(*) FROM user;'
    DATABASE_NAME = 'default'

    def __init__(self):
        super(UserManager, self).__init__()

    def create_table(self):
        db = DatabaseManager.instance(UserManager.DATABASE_NAME)
        if not db.table_exists('user'):
            db.query(UserManager.CREATE_TABLE_QUERY)

    def drop_table(self):
        db = DatabaseManager.instance(UserManager.DATABASE_NAME)
        db.query(UserManager.DROP_TABLE_QUERY)

    def create_object(self, obj):
        db = DatabaseManager.instance(UserManager.DATABASE_NAME)
        try:
            pwd_hash = pwd_context.encrypt(obj.password)
            db.query(UserManager.CREATE_OBJECT_QUERY, (None, obj.username, pwd_hash, int(obj.admin), time.time(),))
            user_data = db.query(UserManager.GET_OBJECT_QUERY, (obj.username,)).next()
            obj.id = user_data['id']
            obj.created = user_data['created']
        except Exception as e:
            print('Exception: %s' % e)
            raise ValueError('username already exists.')

    def delete_object(self, obj):
        if obj.id:
            db = DatabaseManager.instance(UserManager.DATABASE_NAME)
            db.query(UserManager.DELETE_OBJECT_QUERY, (obj.id,))
            obj.id = None
            obj.created = None
            return True
        else:
            obj.id = None
            obj.created = None
            return False

    def update_object(self, obj):
        if obj.id:
            try:
                pwd_hash = pwd_context.encrypt(obj.password)
                db = DatabaseManager.instance(UserManager.DATABASE_NAME)
                db.query(UserManager.UPDATE_OBJECT_QUERY, (obj.username, pwd_hash, int(obj.admin), obj.id,))
            except Exception as e:
                print('Exception: %s' % e)
                raise ValueError('User with id does not exist.')

    def get(self, **kwargs):
        db = DatabaseManager.instance(UserManager.DATABASE_NAME)
        try:
            if 'id' in kwargs and 'username' in kwargs:
                data = db.query('SELECT * FROM user WHERE id=? AND username=?;', (kwargs['id'], kwargs['username'],)).next()
            elif 'id' in kwargs:
                data = db.query('SELECT * FROM user WHERE id=?;', (kwargs['id'],)).next()
            elif 'username' in kwargs:
                data = db.query('SELECT * FROM user WHERE username=?;', (kwargs['username'],)).next()
            else:
                raise ValueError("Missing 'id' or 'username' kwargs.")

            if data:
                return User(data['username'], None, bool(data['admin']), data['id'], data['created'])
            else:
                return None
        except:
            return None

    def authenticate(self, obj, password):
        try:
            db = DatabaseManager.instance(UserManager.DATABASE_NAME)
            data = db.query(UserManager.GET_OBJECT_QUERY, (obj.username,)).next()
            if pwd_context.verify(password, data['password']):
                return True
            else:
                return False
        except:
            return False

    def all(self):
        db = DatabaseManager.instance(UserManager.DATABASE_NAME)
        results = []

        for data in db.query('SELECT * FROM user;'):
            results.append(User(data['username'], None, bool(data['admin']), data['id'], data['created']))

        return results

    def count(self):
        db = DatabaseManager.instance(UserManager.DATABASE_NAME)
        return db.query(UserManager.COUNT_OBJECT_QUERY).next()['COUNT(*)']

class User(Model):
    users = UserManager()

    def __init__(self, username, password, admin, user_id=None, created=None):
        self.id = user_id
        self.username = username
        self.password = password
        self.admin = admin
        self.created = created

    def __repr__(self):
        return '<User id: {0}, username: {1}, password: {2}, admin: {3}, created: {4}>'.format(self.id, self.username, self.password, self.admin, self.created)

    def save(self):
        if self.id:
            User.users.update_object(self)
        else:
            User.users.create_object(self)
            # Now get the id of the newly created object, query it, and get the creation time.

    def authenticate(self, password):
        return User.users.authenticate(self, password)

    def delete(self):
        return User.users.delete_object(self)

    def database_name(self):
        return 'default'
