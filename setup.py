import uuid
import os

from flask_pymongo import PyMongo, wrappers
from database import mongo

from models.user import User

if os.path.exists(".installed"):
    raise "webdock is installed"

print("Webdock installation")
username = input("username: ")
password = input("password: ")
uid = uuid.uuid4()
level = User.ADMIN



user = User(username, password, level, uid)
db: wrappers.Collection = mongo.db.users
db.insert_one(user.__dict__)

open(".installed", "wb").close()