from flask import Flask, url_for, request, session, render_template, redirect, Blueprint
from flask_pymongo import PyMongo, wrappers
from flask_uuid import FlaskUUID
from database import mongo

from models.user import User

from util import deserialize_json

class Users(object):
    def __init__(self):
        pass
    
    @staticmethod
    def find_by_name(username):
        db: wrappers.Collection = mongo.db.users
        user: User = deserialize_json(User, db.find_one({ "username": username }))
        return user
    
    @staticmethod
    def find_by_uuid(uid):
        db: wrappers.Collection = mongo.db.users
        user: User = deserialize_json(User, db.find_one({ "uuid": uid }))
        return user
    