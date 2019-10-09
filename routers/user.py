import uuid

from flask import Flask, url_for, request, session, render_template, redirect, Blueprint
from flask_pymongo import PyMongo, wrappers
from flask_uuid import FlaskUUID

from classes.user.user import Users as userAPI

from models.user import User
from database import mongo
from util import deserialize_json, login_required

user_api = Blueprint("user_api", __name__)

#@user_api.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("user/signup.html")

    username = request.form["username"]
    password = request.form["password"]

    if "../" in username:
        return render_template("user/signup.html")

    result = userAPI.find_by_name(username)
    if result != None:
        return "exist user"

    u_uuid = userAPI.add(username, password, 0)

    session["username"] = username
    session["uuid"] = str(u_uuid)
    session["level"] = 0

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

        result = userAPI.signin(username, password)
        if result == None:
            return "<script>alert('user not found'); history.back(-1);</script>"

        session["username"] = username
        session["uuid"] = str(result.uuid)
        session["level"] = result.level

    return redirect("/docker")

@user_api.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect("/index")