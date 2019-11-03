import uuid

from flask import Flask, url_for, request, session, render_template, redirect, Blueprint
from flask_pymongo import PyMongo, wrappers
from flask_uuid import FlaskUUID

from database import mongo

from classes.api.auth import AuthAPI
from classes.api.dockerimage import DockerImageAPI
from classes.api.dockercontainer import DockerContainerAPI
from classes.api.filesystem import FilesystemAPI

from classes.user.user import Users

from models.user import User
from models.image import Image
from models.container import Container
from models.token import Token

from util import deserialize_json, json_result, xtoken_required, xtoken_valid, xtoken_user, admin_required

api_api = Blueprint("api_api", __name__, url_prefix="/api")
authapi = AuthAPI()
fsapi = FilesystemAPI("./upload/")

@api_api.route("/")
@api_api.route("/v1")
@api_api.route("/v1/")
def api_index():
    return render_template("/api/index.html")

@api_api.route("/v1/request_auth", methods=["POST"])
def api_request_auth():
    username = request.form["username"]
    password = request.form["password"]
    result = authapi.signin(username, password)
    if result == "":
        return json_result(-1, "login failed")
    return json_result(0, result)

@api_api.route("/v1/images", methods=["GET"])
@xtoken_required
def api_images():
    user = xtoken_user(AuthAPI.getXToken())
    img_db: wrappers.Collection = mongo.db.images
    image: list = deserialize_json(Image, img_db.find({ "uid": user.uuid }))
    if len(image) == 0:
        return json_result(-1, "image not found")
    return json_result(0, image)
    
@api_api.route("/v1/containers", methods=["GET"])
@xtoken_required
def api_containers():
    user = xtoken_user(AuthAPI.getXToken())
    con_db: wrappers.Collection = mongo.db.containers
    container: list = deserialize_json(Container, con_db.find({ "uid": user.uuid }))
    if len(container) == 0:
        return json_result(-1, "container not found")
    return json_result(0, container)

@api_api.route("/v1/image/rm/<uuid:sid>", methods=["GET"])
@xtoken_required
def api_image_rm(sid):
    user: User = xtoken_user(AuthAPI.getXToken())
    db: wrappers.Collection = mongo.db.images
    image: Image = deserialize_json(Image, db.find_one({ "uid": user.uuid, "uuid": str(sid) }))
    try:
        DockerImageAPI.delete(image.image_id)
        return json_result(0, "image removed")
    except:
        return json_result(-1, "image not found")

@api_api.route("/v1/container/rm/<uuid:sid>", methods=["GET"])
@xtoken_required
def api_container_rm(sid):
    user: User = xtoken_user(AuthAPI.getXToken())
    db: wrappers.Collection = mongo.db.images
    container: Container = deserialize_json(Container, db.find_one({ "uid": user.uuid, "uuid": str(sid) }))
    try:
        DockerContainerAPI.remove(container.container_id)
        return json_result(0, "container removed")
    except:
        return json_result(-1, "container not found")

@api_api.route("/v1/image/<uuid:sid>", methods=["GET"])
@xtoken_required
def api_image_detail(sid: uuid.UUID):
    user: User = xtoken_user(AuthAPI.getXToken())
    db: wrappers.Collection = mongo.db.images
    image: Image = deserialize_json(Image, db.find_one({ "uid": user.uuid, "uuid": str(sid) }))
    return json_result(0, image)

@api_api.route("/v1/container/<uuid:sid>", methods=["GET"])
@xtoken_required
def api_container_detail(sid: uuid.UUID):
    user: User = xtoken_user(AuthAPI.getXToken())
    db: wrappers.Collection = mongo.db.images
    container: Container = deserialize_json(Container, db.find_one({ "uid": user.uuid, "uuid": str(sid) }))
    return json_result(0, container)

@api_api.route("/v1/image/run/<uuid:sid>/<int:port>", methods=["GET"])
@xtoken_required
def api_image_run(sid: uuid.UUID, port: int):
    user: User = xtoken_user(AuthAPI.getXToken())
    db: wrappers.Collection = mongo.db.images
    image: Image = deserialize_json(Image, db.find_one({ "uid": user.uuid, "uuid": str(sid) }))
    try:
        DockerImageAPI.run(image.tag, "", port)
        return json_result(0, "image run")
    except:
        return json_result(-1, "image not found")

@api_api.route("/v1/container/start/<uuid:sid>", methods=["GET"])
@xtoken_required
def api_container_start(sid: uuid.UUID):
    user: User = xtoken_user(AuthAPI.getXToken())
    db: wrappers.Collection = mongo.db.images
    container: Container = deserialize_json(Container, db.find_one({ "uid": user.uuid, "uuid": str(sid) }))
    try:
        DockerContainerAPI.start(container.container_id)
        return json_result(0, "container start")
    except:
        return json_result(-1, "container not found")

@api_api.route("/v1/container/stop/<uuid:sid>", methods=["GET"])
@xtoken_required
def api_container_stop(sid: uuid.UUID):
    user: User = xtoken_user(AuthAPI.getXToken())
    db: wrappers.Collection = mongo.db.images
    container: Container = deserialize_json(Container, db.find_one({ "uid": user.uuid, "uuid": str(sid) }))
    try:
        DockerContainerAPI.stop(container.container_id)
        return json_result(0, "container stop")
    except:
        return json_result(-1, "container not found")

@api_api.route("/v1/directory", methods=["POST"])
@xtoken_required
def api_directory():
    path = request.form["path"]
    if path == None:
        path = "."
    if "../" in path:
        return redirect("/v1/error")
    user = xtoken_user(AuthAPI.getXToken())
    return fsapi.listing(user.username, path)

@api_api.route("/v1/directory/upload", methods=["POST"])
@xtoken_required
def api_directory_upload():
    path = request.form["path"]
    data = request.files["data"]
    if not path or "../" in path:
        return redirect("/v1/error")
    user = xtoken_user(AuthAPI.getXToken())
    return fsapi.write(user.username, path, data)

@api_api.route("/v1/directory/download", methods=["POST"])
@xtoken_required
def api_directory_download():
    path = request.form["path"]
    if not path or "../" in path:
        return redirect("/v1/error")
    user = xtoken_user(AuthAPI.getXToken())
    return fsapi.read(user.username, path)

@api_api.route("/v1/directory/remove", methods=["POST"])
@xtoken_required
def api_directory_remove():
    path = request.form["path"]
    if "../" in path:
        return redirect("/v1/error")
    user = xtoken_user(AuthAPI.getXToken())
    return fsapi.rm(user.username + "/" + path)

@api_api.route("/v1/directory/removedir", methods=["POST"])
@xtoken_required
def api_directory_removedir():
    path = request.form["path"]
    if "../" in path:
        return redirect("/v1/error")
    user = xtoken_user(AuthAPI.getXToken())
    return fsapi.rmdir(user.username, path)

@api_api.route("/v1/users", methods=["GET"])
@admin_required
def api_users():
    return json_result(0, Users.all())

@api_api.route("/v1/error")
def api_error():
    return json_result(-1, "error")