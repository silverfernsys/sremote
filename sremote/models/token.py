# -*- coding: utf-8 -*-
import binascii
import os
import time
from model import Manager, Model
from user import User 
from database import Database, DatabaseManager

class TokenManager(Manager):
    CREATE_TABLE_QUERY = """CREATE TABLE token (id INTEGER PRIMARY KEY AUTOINCREMENT,
                userid INTEGER, token TEXT, created TIMESTAMP, UNIQUE(token), UNIQUE(userid));"""
    DROP_TABLE_QUERY = """DROP TABLE token;"""
    CREATE_OBJECT_QUERY = """INSERT INTO token VALUES (?,?,?,?);"""
    DELETE_OBJECT_QUERY = """DELETE FROM token WHERE id=?;"""
    UPDATE_OBJECT_QUERY = ''
    GET_OBJECT_QUERY = 'SELECT * FROM token WHERE token=?;'
    COUNT_OBJECT_QUERY = 'SELECT COUNT(*) FROM token;'
    DATABASE_NAME = 'default'

    def __init__(self):
        super(TokenManager, self).__init__()

    def create_table(self):
        db = DatabaseManager.instance(TokenManager.DATABASE_NAME)
        if not db.table_exists('token'):
            db.query(TokenManager.CREATE_TABLE_QUERY)

    def drop_table(self):
        db = DatabaseManager.instance(TokenManager.DATABASE_NAME)
        db.query(TokenManager.DROP_TABLE_QUERY)

    def create_object(self, obj):
        db = DatabaseManager.instance(TokenManager.DATABASE_NAME)
        try:
            if not self.get_token_for_user(obj.user):
                query_data = (None, obj.user.id, obj.token, time.time(),)
                db.query(TokenManager.CREATE_OBJECT_QUERY, params=query_data)
                token_data = db.query(TokenManager.GET_OBJECT_QUERY, (obj.token,)).nextresult()
                obj.id = token_data['id']
                obj.created = token_data['created']
            else:
                raise ValueError('token for this user already exists')
        except ValueError as e:
            raise e

    def delete_object(self, obj):
        if obj.id:
            db = DatabaseManager.instance(TokenManager.DATABASE_NAME)
            db.query(TokenManager.DELETE_OBJECT_QUERY, (obj.id,))
        obj.id = None
        obj.created = None

    def get_token_for_user(self, user):
        if user.id:
            try:
                db = DatabaseManager.instance(TokenManager.DATABASE_NAME)
                query = 'SELECT * FROM token WHERE userid=?;'
                token_data = db.query(query, (user.id,)).nextresult()
                return Token(user=user, token_id=token_data['id'], token=token_data['token'], created=token_data['created'])
            except:
                return None
        else:
            raise ValueError('User has no id.')

    def get(self, **kwargs):
        if 'token' in kwargs:
            join = """
            SELECT user.id AS user_id,
            user.username,
            user.admin,
            user.created AS user_created,
            token.id AS token_id,
            token.token,
            token.created AS token_created
            FROM user INNER JOIN token ON token.userid = user.id WHERE token.token=?;
            """
            db = DatabaseManager.instance(TokenManager.DATABASE_NAME)
            try:
                data = db.query(join, (kwargs['token'],)).nextresult()
                user = User(data['username'], None, bool(data['admin']), data['user_id'], data['user_created'])
                token = Token(user, data['token_id'], data['token'], data['token_created'])
                return token
            except:
                return None
        else:
            raise ValueError("Expecting 'token' in arguments.")

    def all(self):
        join = """
        SELECT user.id AS user_id,
        user.username,
        user.admin,
        user.created AS user_created,
        token.id AS token_id,
        token.token,
        token.created AS token_created
        FROM user INNER JOIN token ON token.userid = user.id ORDER BY user.username, token.created;
        """
        results = []

        db = DatabaseManager.instance(TokenManager.DATABASE_NAME)
        for data in db.query(join):
            user = User(data['username'], None, bool(data['admin']), data['user_id'], data['user_created'])
            token = Token(user, data['token_id'], data['token'], data['token_created'])
            results.append(token)

        return results

    def update_object(self, obj):
        pass

    def count(self):
        db = DatabaseManager.instance(TokenManager.DATABASE_NAME)
        return db.query(TokenManager.COUNT_OBJECT_QUERY, params=None, fetchall=False).nextresult()['COUNT(*)']

class Token(Model):
    _tokens = None

    def __init__(self, user=None, token_id=None, token=None, created=None):
        if Token.tokens is None:
            Token.tokens = UserManager()

        self.id = token_id
        self.user = user

        if token == None:
            self.token = binascii.hexlify(os.urandom(20)).decode()
        else:
            self.token = token
        self.created = created

    @classmethod
    def tokens(self):
        if Token._tokens is None:
            Token._tokens = TokenManager()
        return Token._tokens

    def __repr__(self):
        return '<Token id: {0}, user: {1}, token: {2}, created: {3}>'.format(self.id, self.user, self.token, self.created)

    def save(self):
        Token.tokens().create_object(self)

    def delete(self):
        Token.tokens().delete_object(self)

    def database_name(self):
        return 'default'
