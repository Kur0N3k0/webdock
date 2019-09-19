import uuid
import time
import os
import shutil
import json
import glob

from flask import Flask, url_for, request, session, render_template, redirect, Blueprint, send_file
from flask_pymongo import PyMongo, wrappers
from flask_uuid import FlaskUUID
from werkzeug.utils import secure_filename

from models.image import Image
from models.dockerfile import Dockerfile
from database import mongo
from util import deserialize_json, login_required, json_result

from classes.api.filesystem import FilesystemAPI

userfile_api = Blueprint("userfile_api", __name__)

userfile_base = "./upload/"
filesystem = FilesystemAPI(userfile_base)

@userfile_api.route("/file", methods=["GET"])
@userfile_api.route("/file/", methods=["GET"])
@login_required
def userfile():
    base = userfile_base + session["username"] + "/"
    if not os.path.exists(base):
        os.mkdir(base)
        f = open(base + "README.txt", "w")
        f.write("Hello world")
        f.close()

    result = filesystem.listing(session["username"], "")
    return render_template("userfile/list.html", result=result)

@userfile_api.route("/file/<path>", methods=["GET"])
@login_required
def userfile_listing(path: str):
    base = userfile_base + session["username"] + "/"
    result = { "is_base": False, "path": path, "dir": [], "file": [] }

    if "../" in path:
        return render_template("userfile/list.html", result=result)
    if os.path.isfile(base + path):
        return send_file(base + path)

    result = filesystem.listing(session["username"], path)
    result["is_base"] = False

    return render_template("userfile/list.html", result=result)

@userfile_api.route("/file/mkdir", methods=["POST"])
def userfile_mkdir():
    base = userfile_base + session["username"] + "/"
    path = base + request.form["dir"]

    if "../" in path:
        return json_result(-1, "invalid path")
    if not os.path.exists(path):
        os.makedirs(path)
        return json_result(0, "success")

    return json_result(-1, "exist path")

@userfile_api.route("/file/rmdir", methods=["POST"])
def userfile_rmdir():
    base = userfile_base + session["username"] + "/"
    path = base + request.form["dir"]

    if "../" in path:
        return json_result(-1, "invalid path")
    if not os.path.exists(path):
        return json_result(-1, "path not exist")

    os.removedirs(path)
    return json_result(0, "success")

@userfile_api.route("/file/rm", methods=["POST"])
def userfile_rm():
    base = userfile_base + session["username"] + "/"
    path = base + request.form["file"]

    if "../" in path:
        return json_result(-1, "invalid path")
    if not os.path.exists(path):
        return json_result(-1, "file not exist")
    if not os.path.isfile(path):
        return json_result(-1, "invalid type")

    os.remove(path)
    return json_result(0, "success")

@userfile_api.route("/file/mv", methods=["POST"])
def userfile_mv():
    base = userfile_base + session["username"] + "/"
    src = base + request.form["src"]
    dst = base + request.form["dst"]

    if "../" in src or "../" in dst:
        return json_result(-1, "invalid path")
    if not os.path.exists(src) or not os.path.exists(dst):
        return json_result(-1, "invalid path")
    
    shutil.move(src, dst)
    return json_result(0, "success")

@userfile_api.route("/file/cp", methods=["POST"])
def userfile_cp():
    base = userfile_base + session["username"] + "/"
    src = base + request.form["src"]
    dst = base + request.form["dst"]

    if "../" in src or "../" in dst:
        return json_result(-1, "invalid path")
    if not os.path.exists(src):
        return json_result(-1, "invalid path")
    
    shutil.copy(src, dst)
    return json_result(0, "success")

