import uuid

from flask import Flask, url_for, request, session, render_template, redirect, Blueprint
from flask_pymongo import PyMongo, wrappers
from flask_uuid import FlaskUUID
from werkzeug.utils import secure_filename

from models.dockers import Dockers
from models.dockerfile import Dockerfile
from database import mongo

dockerfile_api = Blueprint("dockerfile_api", __name__)

login_check = lambda: session.get("username") != None

@dockerfile_api.route("/dockerfile")
@dockerfile_api.route("/dockerfile/list")
def dockerfile():
    if login_check() == False:
        return render_template("fail.html")

    db: wrappers.Collection = mongo.db.dockerfile
    uid: uuid.UUID = session.get("uuid")

    result: Dockerfile = db.find({ "uuid": uid })

    return render_template("docker/list.html")

@dockerfile_api.route("/dockerfile/upload", methods=["POST"])
def dockerfile_upload():
    if login_check() == False:
        return render_template("fail.html")

    f = request.files["file"]
    fn = "/upload/" + secure_filename(f.filename)
    f.save(fn)

    uid = session.get("uuid")
    fn_uuid = uuid.uuid4()
    db: wrappers.Collection = mongo.db.dockerfile
    db.insert_one(Dockerfile(uid, fn, fn_uuid).__dict__)
    
    return ""

@dockerfile_api.route("/dockerfile/view/<uuid:fn_uuid>")
def dockerfile_view(fn_uuid: uuid.UUID):
    if login_check() == False:
        return render_template("fail.html")

    db: wrappers.Collection = mongo.db.dockerfile
    uid = session.get("uuid")
    result: Dockerfile = db.find_one({ "uid": uid, "uuid": fn_uuid })
    if result == None:
        return render_template("fail.html")

    with open(result.path, "rb") as f:
        df = f.read()

    return ""

@dockerfile_api.route("/dockerfile/save")
def dockerfile_save():

    return ""