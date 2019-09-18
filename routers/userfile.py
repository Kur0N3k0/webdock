import uuid
import time
import os
import json
import glob

from flask import Flask, url_for, request, session, render_template, redirect, Blueprint, send_file
from flask_pymongo import PyMongo, wrappers
from flask_uuid import FlaskUUID
from werkzeug.utils import secure_filename

from models.image import Image
from models.dockerfile import Dockerfile
from database import mongo
from util import deserialize_json, login_required

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

@userfile_api.route("/file/mkdir", methods=["GET"])
def userfile_mkdir():
    
    return ""

@userfile_api.route("/file/rmdir", methods=["GET"])
def userfile_rmdir():
    # listing
    return ""

@userfile_api.route("/file/rm", methods=["GET"])
def userfile_rm():
    # listing
    return ""

@userfile_api.route("/file/mv", methods=["GET"])
def userfile_mv():
    # listing
    return ""

@userfile_api.route("/file/cp", methods=["GET"])
def userfile_cp():
    # listing
    return ""

