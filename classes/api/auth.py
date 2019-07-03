from classes.api.api import API
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

        t = time.time()
        xtoken = hashlib.sha1(tenant + str(t)).hexdigest()
        token = Token(tenant, time.time() + 7200, xtoken)

        db.insert_one(token.__dict__)

        return token.__dict__