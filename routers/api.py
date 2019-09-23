import uuid

from flask import Flask, url_for, request, session, render_template, redirect, Blueprint
from flask_pymongo import PyMongo, wrappers
from flask_uuid import FlaskUUID

from database import mongo

from classes.api.auth import AuthAPI
from classes.api.dockerimage import DockerImageAPI
from classes.api.dockercontainer import DockerContainerAPI
from classes.api.filesystem import FilesystemAPI

from models.user import User
from models.image import Image
from models.container import Container
from models.token import Token

from util import deserialize_json, json_result, xtoken_required, xtoken_valid, xtoken_user

api_api = Blueprint("api_api", __name__, url_prefix="/api")
authapi = AuthAPI()
fsapi = FilesystemAPI("./upload/")

@api_api.route("/")
@api_api.route("/v1")
@api_api.route("/v1/")
def api_index():
    return "WebDock api v1.0 is alive!"

@api_api.route("/v1/request_auth", methods=["POST"])
def api_request_auth():
    tenant = request.form["tenant"]
    password = request.form["password"]
    result = authapi.signin(tenant, password)
    return json_result(0, result)

@api_api.route("/v1/images")
@xtoken_required
def api_images():
    user = xtoken_user(AuthAPI.getXToken())
    img_db: wrappers.Collection = mongo.db.images
    image: list = deserialize_json(Image, img_db.find({ "uid": user.uuid }))
    return json_result(0, image)
    
@api_api.route("/v1/containers")
@xtoken_required
def api_containers():
    user = xtoken_user(AuthAPI.getXToken())
    con_db: wrappers.Collection = mongo.db.containers
    container: list = deserialize_json(Container, con_db.find({ "uid": user.uuid }))
    return json_result(0, container)

@api_api.route("/v1/image/rm/<uuid:sid>")
@xtoken_required
def api_image_rm(sid):
    user: User = xtoken_user(AuthAPI.getXToken())
    db: wrappers.Collection = mongo.db.images
    image: Image = deserialize_json(Image, db.find_one({ "uid": user.uuid, "uuid": str(sid) }))
    DockerImageAPI.delete(image.image_id)
    return json_result(0, "image removed")

@api_api.route("/v1/container/rm/<uuid:sid>")
@xtoken_required
def api_container_rm(sid):
    user: User = xtoken_user(AuthAPI.getXToken())
    db: wrappers.Collection = mongo.db.images
    container: Container = deserialize_json(Container, db.find_one({ "uid": user.uuid, "uuid": str(sid) }))
    DockerContainerAPI.remove(container.container_id)
    return json_result(0, "container removed")

@api_api.route("/v1/image/<uuid:sid>")
@xtoken_required
def api_image_detail(sid: uuid.UUID):
    user: User = xtoken_user(AuthAPI.getXToken())
    db: wrappers.Collection = mongo.db.images
    image: Image = deserialize_json(Image, db.find_one({ "uid": user.uuid, "uuid": str(sid) }))
    return json_result(0, image)

@api_api.route("/v1/container/<uuid:sid>")
@xtoken_required
def api_container_detail(sid: uuid.UUID):
    user: User = xtoken_user(AuthAPI.getXToken())
    db: wrappers.Collection = mongo.db.images
    container: Container = deserialize_json(Container, db.find_one({ "uid": user.uuid, "uuid": str(sid) }))
    return json_result(0, container)

@api_api.route("/v1/image/run/<uuid:sid>/<int:port>")
@xtoken_required
def api_image_run(sid: uuid.UUID, port: int):
    user: User = xtoken_user(AuthAPI.getXToken())
    db: wrappers.Collection = mongo.db.images
    image: Image = deserialize_json(Image, db.find_one({ "uid": user.uuid, "uuid": str(sid) }))
    DockerImageAPI.run(image.tag, "", port)
    return json_result(0, "image run")

@api_api.route("/v1/container/start/<uuid:sid>")
@xtoken_required
def api_container_start(sid: uuid.UUID):
    user: User = xtoken_user(AuthAPI.getXToken())
    db: wrappers.Collection = mongo.db.images
    container: Container = deserialize_json(Container, db.find_one({ "uid": user.uuid, "uuid": str(sid) }))
    DockerContainerAPI.start(container.container_id)
    return json_result(0, "container start")

@api_api.route("/v1/container/stop/<uuid:sid>")
@xtoken_required
def api_container_stop(sid: uuid.UUID):
    user: User = xtoken_user(AuthAPI.getXToken())
    db: wrappers.Collection = mongo.db.images
    container: Container = deserialize_json(Container, db.find_one({ "uid": user.uuid, "uuid": str(sid) }))
    DockerContainerAPI.stop(container.container_id)
    return json_result(0, "container stop")

@api_api.route("/v1/directory")
@xtoken_required
def api_directory():
    path = request.args.get("path")
    if "../" in path:
        return redirect("/v1/error")
    user = xtoken_user(AuthAPI.getXToken())
    return fsapi.listing(user.username, path)

@api_api.route("/v1/error")
def api_error():
    return json_result(-1, "error")