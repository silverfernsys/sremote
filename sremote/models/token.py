# -*- coding: utf-8 -*-
import binascii
import os
import time
from model import Manager, Model
from database import Database, DatabaseManager

class TokenManager(Manager):
    CREATE_TABLE_QUERY = """CREATE TABLE token (id INTEGER PRIMARY KEY AUTOINCREMENT,
                userid INTEGER, token TEXT, created TIMESTAMP, UNIQUE(token), UNIQUE(userid));"""
    DROP_TABLE_QUERY = """DROP TABLE token;"""
    CREATE_OBJECT_QUERY = """INSERT INTO token VALUES (?,?,?,?);"""
    DELETE_OBJECT_QUERY = """DELETE FROM token WHERE id=?;"""
    UPDATE_OBJECT_QUERY = ''
    GET_OBJECT_QUERY = 'SELECT * FROM token WHERE userid=?;'
    COUNT_OBJECT_QUERY = 'SELECT COUNT(*) FROM token;'
    DATABASE_NAME = 'default'

    def __init__(self):
        super(TokenManager, self).__init__()

    def create_table(self):
        db = DatabaseManager.instance(TokenManager.DATABASE_NAME)
        db.query(TokenManager.CREATE_TABLE_QUERY)

    def drop_table(self):
        db = DatabaseManager.instance(TokenManager.DATABASE_NAME)
        db.query(TokenManager.DROP_TABLE_QUERY)

    def create_object(self, obj):
        db = DatabaseManager.instance(TokenManager.DATABASE_NAME)
        if obj.user.id is None:
            raise ValueError('User.id is None')
        try:
            db.query(TokenManager.CREATE_OBJECT_QUERY, (None, obj.user.id, obj.token, time.time(),))
            token_data = db.query(TokenManager.GET_OBJECT_QUERY, (obj.user.id,)).next()
            obj.id = token_data['id']
            obj.created = token_data['created']
        except Exception as e:
            raise ValueError('token for this user already exists.')

    def delete_object(self, obj):
        if obj.id:
            db = DatabaseManager.instance(TokenManager.DATABASE_NAME)
            db.query(TokenManager.DELETE_OBJECT_QUERY, (obj.id,))
        obj.id = None
        obj.created = None

    def get_token_for_user(self, user):
        if user.id:
            db = DatabaseManager.instance(TokenManager.DATABASE_NAME)
            token_data = db.query(TokenManager.GET_OBJECT_QUERY, (user.id,)).next()
            return Token(user=user, token_id=token_data['id'], token=token_data['token'], created=token_data['created'])
        else:
            raise ValueError('User has no id.')

    def get(self, **kwargs):
        pass
        
    def all(self):
        pass

    def update_object(self, obj):
        pass

    def count(self):
        db = DatabaseManager.instance(TokenManager.DATABASE_NAME)
        return db.query(TokenManager.COUNT_OBJECT_QUERY, params=None, fetchall=False).next()['COUNT(*)']

class Token(Model):
    tokens = TokenManager()

    def __init__(self, user=None, token_id=None, token=None, created=None):
        self.id = token_id
        self.user = user

        if token == None:
            self.token = binascii.hexlify(os.urandom(20)).decode()
        else:
            self.token = token
        self.created = created

    def save(self):
        if not self.id:
            Token.tokens.create_object(self)

    def delete(self):
        Token.tokens.delete_object(self)

    def database_name(self):
        return 'default'
