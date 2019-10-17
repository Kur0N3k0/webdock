from functools import wraps
from flask import session, redirect, request
from flask_pymongo import pymongo, wrappers

from database import mongo
#from classes.api.auth import AuthAPI
from models.token import Token
from models.user import User

import string, random, json, time

def login_required(func):
    @wraps(func)
    def deco(*args, **kwargs):
        if session.get("username") == None:
            return redirect("/signin")
        return func(*args, **kwargs)
    return deco

def admin_required(func):
    @wraps(func)
    def deco(*args, **kwargs):
        if session.get("username") == None:
            return redirect("/signin")
        if session.get("level") == 0:
            return redirect("/")
        return func(*args, **kwargs)
    return deco

def xtoken_required(func):
    @wraps(func)
    def deco(*args, **kwargs):
        token = request.headers.get("X-Access-Token")
        if not token or not xtoken_valid(token):
            return redirect("/api/v1/error")
        return func(*args, **kwargs)
    return deco

def xtoken_valid(xtoken):
    token_db: wrappers.Collection = mongo.db.token
    token: Token = deserialize_json(Token, token_db.find_one({ "token": xtoken }))
    if not token:
        return False
    
    if token.expire_date <= time.time():
        return False

    return True

def xtoken_user(xtoken):
    token_db: wrappers.Collection = mongo.db.token
    token: Token = deserialize_json(Token, token_db.find_one({ "token": xtoken }))
    db: wrappers.Collection = mongo.db.users
    return deserialize_json(User, db.find_one({ "uuid": token.tenant }))

def sanitize_input(data):

    return data

def randomString(stringLength):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def error(msg):
    return json.dumps([{ "errorDetail": msg }])

def json_result(code, msg):
    if isinstance(msg, list):
        msg = [ item.__dict__ for item in msg ]
        return json.dumps({ "code": code, "msg": msg })
        
    try:
        return json.dumps({ "code": code, "msg": msg.__dict__ })
    except:
        return json.dumps({ "code": code, "msg": msg })

def deserialize_json(cls=None, data=None):
    if data == None:
        return None
        
    if isinstance(data, list):
        r = []
        for item in data:
            instance = object.__new__(cls)
            for key, value in item.items():
                if key == "_id":
                    continue
                setattr(instance, key, value)
            r += [instance]
        return r
    elif isinstance(data, pymongo.cursor.Cursor):
        cursor: pymongo.cursor.Cursor = data
        r = []
        for item in cursor:
            instance = object.__new__(cls)
            for key, value in item.items():
                if key == "_id":
                    continue
                setattr(instance, key, value)
            r += [instance]
        return r
    else:
        instance = object.__new__(cls)
        for key, value in data.items():
            if key == "_id":
                continue
            setattr(instance, key, value)

        return instance