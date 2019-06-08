import uuid

from flask import Flask, url_for, request, session, render_template, redirect, Blueprint
from flask_pymongo import PyMongo, wrappers
from flask_uuid import FlaskUUID

from models.user import User
from models.payment import Payment
from database import mongo
from util import deserialize_json, login_required

user_api = Blueprint("user_api", __name__)

@user_api.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("user/signup.html")

    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db: wrappers.Collection = mongo.db.users
        result = db.find_one({ "username": username })
        if result != None:
            return "exist user"

        u_uuid = uuid.uuid4()
        user = User(username, password, 0, u_uuid)
        db.insert_one(user.__dict__)

        session["username"] = username
        session["uuid"] = u_uuid

    return redirect("/docker")

@user_api.route("/signin", methods=["GET", "POST"])
def signin():
    """
    POST
    :param username: username
    :param password: password
    """
    if request.method == "GET":
        return render_template("user/signin.html")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db: wrappers.Collection = mongo.db.users
        result: User = deserialize_json(User, db.find_one({ "username": username, "password": password }))
        if result == None:
            return "<script>alert('user not found'); history.back(-1);</script>"

        session["username"] = username
        session["uuid"] = result.uuid
        session["level"] = result.level

    return redirect("/docker")

@user_api.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect("/index")