from flask import Flask, url_for, request, session, render_template, redirect, Blueprint
from flask_pymongo import PyMongo, wrappers
from flask_uuid import FlaskUUID
from database import mongo
from models.user import User
from util import deserialize_json
import uuid

class Users(object):
    def __init__(self):
        pass
    
    @staticmethod
    def all():
        db: wrappers.Collection = mongo.db.users
        user: list = deserialize_json(User, db.find())
        return user

    @staticmethod
    def add(username, password, level):
        db: wrappers.Collection = mongo.db.users
        result = db.find_one({ "username": username })
        if result != None:
            return False
        
        u_uuid = uuid.uuid4()
        user = User(username, password, level, u_uuid)
        db.insert_one(user.__dict__)
        return str(u_uuid)
    
    @staticmethod
    def remove_by_name(username):
        db: wrappers.Collection = mongo.db.users
        db.delete_one({ "username": username })
        return True
    
    @staticmethod
    def remove_by_uuid(uid):
        db: wrappers.Collection = mongo.db.users
        db.delete_one({ "uuid": str(uid) })
        return True

    @staticmethod
    def signin(username, password):
        db: wrappers.Collection = mongo.db.users
        result: User = deserialize_json(User, db.find_one({ "username": username, "password": password }))
        return result

    @staticmethod
    def find_by_name(username):
        db: wrappers.Collection = mongo.db.users
        user: User = deserialize_json(User, db.find_one({ "username": username }))
        return user
    
    @staticmethod
    def find_by_uuid(uid):
        db: wrappers.Collection = mongo.db.users
        user: User = deserialize_json(User, db.find_one({ "uuid": str(uid) }))
        return user

    @staticmethod
    def update_by_uuid(sid, user):
        db: wrappers.Collection = mongo.db.users
        db.update({ "uuid": str(sid) }, user.__dict__)
        return True