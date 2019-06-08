from functools import wraps
from flask import session, redirect
from flask_pymongo import pymongo

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

def deserialize_json(cls=None, data=None):
    if data == None:
        return None
        
    if isinstance(data, list):
        r = []
        for item in data:
            instance = object.__new__(cls)
            for key, value in item.items():
                setattr(instance, key, value)
            r += [instance]
        return r
    elif isinstance(data, pymongo.cursor.Cursor):
        cursor: pymongo.cursor.Cursor = data
        r = []
        for i in range(cursor.count()):
            instance = object.__new__(cls)
            for item in cursor:
                for key, value in item.items():
                    setattr(instance, key, value)
            r += [instance]
        return r
    else:
        instance = object.__new__(cls)
        for key, value in data.items():
            setattr(instance, key, value)

        return instance