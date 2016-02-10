# -*- coding: utf-8 -*-
import time
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
        db.query(UserManager.CREATE_TABLE_QUERY)

    def drop_table(self):
        db = DatabaseManager.instance(UserManager.DATABASE_NAME)
        db.query(UserManager.DROP_TABLE_QUERY)

    def create_object(self, obj):
        db = DatabaseManager.instance(UserManager.DATABASE_NAME)
        if obj.admin:
            admin = 1
        else:
            admin = 0
        try:
            db.query(UserManager.CREATE_OBJECT_QUERY, (None, obj.username, obj.password, admin, time.time(),))
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

    def update_object(self, obj):
        if obj.id:
            if obj.admin:
                admin = 1
            else:
                admin = 0
            try:
                db = DatabaseManager.instance(UserManager.DATABASE_NAME)
                db.query(UserManager.UPDATE_OBJECT_QUERY, (obj.username, obj.password, admin, obj.id,))
            except:
                raise ValueError('User with id does not exist.')

    def get(self, **kwargs):
        pass

    def all(self):
        pass

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
        self.created = None

    def save(self):
        if self.id:
            User.users.update_object(self)
        else:
            User.users.create_object(self)
            # Now get the id of the newly created object, query it, and get the creation time.

    def delete(self):
        User.users.delete_object(self)

    def database_name(self):
        return 'default'
