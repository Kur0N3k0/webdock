from classes.api.api import API
from flask import request
from flask_pymongo import PyMongo, wrappers
from database import mongo
from util import deserialize_json

from models.user import User
from models.token import Token

import time, hashlib

class AuthAPI(API):
    def __init__(self):
        pass
    
    def signin(self, tenant, password):
        db: wrappers.Collection = mongo.db.users
        result: User = deserialize_json(User, db.find_one({ "uuid": tenant, "password": password }))
        if result == None:
            return "", 401

        token_db: wrappers.Collection = mongo.db.token
        result: Token = deserialize_json(Token, token_db.find_one({ "tenant": tenant }))
        if result != None:
            if result.expire_date + 7200 > time.time():
                t = time.time()
                xtoken = hashlib.sha1((tenant + str(t)).encode('utf-8')).hexdigest()
                result = Token(tenant, time.time() + 7200, xtoken)
                token_db.update_one({ "tenant": tenant }, result.__dict__)
        else:
            t = time.time()
            xtoken = hashlib.sha1((tenant + str(t)).encode('utf-8')).hexdigest()
            result = Token(tenant, time.time() + 7200, xtoken)
            token_db.insert_one(result.__dict__)

        return result.__dict__
    
    @staticmethod
    def getXToken():
        return request.headers.get("X-Access-Token")