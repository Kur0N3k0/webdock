import uuid, time, os, shutil, json, glob

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

    result = json.loads(filesystem.listing(session["username"], ""))["msg"]
    result["path"] = result["path"][6:]
    return render_template("userfile/list.html", result=result)

@userfile_api.route("/file/view", methods=["GET"])
@login_required
def userfile_listing():
    base = userfile_base + session["username"] + "/"
    path = request.args.get('path', default="/")
    result = { "is_base": False, "path": path, "dir": [], "file": [] }

    if path == None:
        return render_template("userfile/list.html", result=result)

    if "../" in path:
        return render_template("userfile/list.html", result=result)
    if os.path.isfile(base + path):
        return send_file(base + path)

    result = json.loads(filesystem.listing(session["username"], path))["msg"]
    result["parent"] = os.path.normpath(path + "/..")
    result["path"] = secure_filename(path)
    result["is_base"] = False

    if path == "/":
        result["is_base"] = True

    return render_template("userfile/list.html", result=result)

@userfile_api.route("/file/mkdir", methods=["POST"])
def userfile_mkdir():
    path = request.form["dir"]
    return filesystem.mkdir(session["username"], path)

@userfile_api.route("/file/rmdir", methods=["POST"])
def userfile_rmdir():
    path = request.form["dir"]
    return filesystem.rmdir(session["username"], path)

@userfile_api.route("/file/rm", methods=["POST"])
def userfile_rm():
    base = userfile_base + session["username"] + "/"
    path = base + request.form["file"]
    return filesystem.rm(path)

@userfile_api.route("/file/mv", methods=["POST"])
def userfile_mv():
    base = userfile_base + session["username"] + "/"
    src = base + request.form["src"]
    dst = base + request.form["dst"]
    return filesystem.mv(src, dst)

@userfile_api.route("/file/cp", methods=["POST"])
def userfile_cp():
    base = userfile_base + session["username"] + "/"
    src = base + request.form["src"]
    dst = base + request.form["dst"]
    return filesystem.cp(src, dst)

@userfile_api.route("/file/upload", methods=["POST"])
def userfile_upload():
    uid = session.get("uuid")
    username = session.get("username")
    path = request.form["path"]

    if "../" in path:
        return json_result(-1, "invalid path")

    f = request.files["file"]
    fn = userfile_base + username + "/" + path + "/" + f.filename
    f.save(fn)
    return json_result(0, "success")