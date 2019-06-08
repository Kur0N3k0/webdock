import uuid
import time
import os
import json

from flask import Flask, url_for, request, session, render_template, redirect, Blueprint
from flask_pymongo import PyMongo, wrappers
from flask_uuid import FlaskUUID
from werkzeug.utils import secure_filename

from models.image import Image
from models.dockerfile import Dockerfile
from database import mongo
from util import deserialize_json, login_required

dockerfile_api = Blueprint("dockerfile_api", __name__)

@dockerfile_api.route("/dockerfile")
@dockerfile_api.route("/dockerfile/list")
@login_required
def dockerfile():
    db: wrappers.Collection = mongo.db.dockerfile
    uid = session.get("uuid")

    result: Dockerfile = deserialize_json(Dockerfile, db.find({ "uid": uid }))
    return render_template("dockerfile/list.html", dockerfiles=result)

@dockerfile_api.route("/dockerfile/upload", methods=["POST"])
@login_required
def dockerfile_upload():
    uid = session.get("uuid")
    fn_uuid = uuid.uuid4()
    path = "upload/" + str(fn_uuid)
    if not os.path.exists(path):
        os.mkdir(path)

    f = request.files["file"]
    fn = "upload/" + str(fn_uuid) + "/Dockerfile"
    f.save(fn)

    db: wrappers.Collection = mongo.db.dockerfile
    db.insert_one(Dockerfile(uid, fn, time.time(), str(fn_uuid)).__dict__)
    
    return ""

@dockerfile_api.route("/dockerfile/view/<uuid:fn_uuid>")
@login_required
def dockerfile_view(fn_uuid: uuid.UUID):
    db: wrappers.Collection = mongo.db.dockerfile
    uid = session.get("uuid")
    result: Dockerfile = deserialize_json(Dockerfile, db.find_one({ "uid": uid, "uuid": str(fn_uuid) }))
    if result == None:
        return render_template("fail.html")

    with open(result.path, "rb") as f:
        df = f.read()

    return df

@dockerfile_api.route("/dockerfile/remove/<uuid:fn_uuid>")
@login_required
def dockerfile_remove(fn_uuid: uuid.UUID):
    uid = session.get("uuid")
    db: wrappers.Collection = mongo.db.dockerfile
    dockerfile: Dockerfile = deserialize_json(Dockerfile, db.find_one_and_delete({ "uid": uid, "uuid": str(fn_uuid) }))
    os.unlink(dockerfile.path)

    return ""

@dockerfile_api.route("/dockerfile/search", methods=["POST"])
@login_required
def dockerfile_search():
    uid = session.get("uuid")
    name = request.form["name"]
    db: wrappers.Collection = mongo.db.dockerfile
    dockerfiles: list = deserialize_json(Dockerfile, db.find({ "uid": uid, "name": name }))

    return json.dumps(dockerfiles)