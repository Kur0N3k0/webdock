from classes.api.api import API
from flask import session
from flask_pymongo import PyMongo, wrappers
from database import mongo
from util import deserialize_json

from models.user import User

class AuthAPI(API):
    def __init__(self):
        pass
    
    def signin(self, tenant, password):
        db: wrappers.Collection = mongo.db.users
        result: User = deserialize_json(User, db.find_one({ "tenant": tenant, "password": password }))
        if result == None:
            return "<script>alert('user not found'); history.back(-1);</script>"

        session["username"] = result.username
        session["uuid"] = str(result.uuid)
        session["level"] = result.level
    
    def logout(self):
        session.clear()