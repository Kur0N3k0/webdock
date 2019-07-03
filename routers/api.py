import uuid

from flask import Flask, url_for, request, session, render_template, redirect, Blueprint
from flask_pymongo import PyMongo, wrappers
from flask_uuid import FlaskUUID

from database import mongo

from classes.api.auth import AuthAPI
from classes.api.dockerimage import DockerImageAPI
from classes.api.dockercontainer import DockerContainerAPI
from classes.api.filesystem import FilesystemAPI

from models.image import Image
from models.container import Container
from models.token import Token

from util import deserialize_json, json_result, xtoken_required

api_api = Blueprint("api_api", __name__, url_prefix="/api")
authapi = AuthAPI()
fsapi = FilesystemAPI()

@api_api.route("/")
@api_api.route("/v1")
@api_api.route("/v1/")
def api_index():
    return "WebDock api is alive!"

@api_api.route("/v1/request_auth", methods=["POST"])
def api_request_auth():
    tenant = request.form["tenant"]
    password = request.form["password"]
    return authapi.signin(tenant, password)

@xtoken_required
@api_api.route("/v1/images")
def api_images():

    pass

@xtoken_required
@api_api.route("/v1/containers")
def api_containers():
    pass

@xtoken_required
@api_api.route("/v1/image/rm")
def api_image_rm():
    pass

@xtoken_required
@api_api.route("/v1/container/rm")
def api_container_rm():
    pass

@xtoken_required
@api_api.route("/v1/image/<uuid:sid>")
def api_image_detail(sid: uuid.UUID):
    pass

@xtoken_required
@api_api.route("/v1/container/<uuid:sid>")
def api_container_detail(sid: uuid.UUID):
    pass

@xtoken_required
@api_api.route("/v1/image/run/<uuid:sid>")
def api_image_run(sid: uuid.UUID):
    pass

@xtoken_required
@api_api.route("/v1/container/start/<uuid:sid>")
def api_container_start(sid: uuid.UUID):
    pass

@xtoken_required
@api_api.route("/v1/container/stop/<uuid:sid>")
def api_container_stop(sid: uuid.UUID):
    pass

@xtoken_required
@api_api.route("/v1/directory/<path:str>")
def api_directory(path: str):
    token_db: wrappers.Collection = mongo.db.token
    
    token = request.headers.get("X-Access-Token")
    if not token:
        return json_result(-1, "Invalid access token")
    token: Token = deserialize_json(Token, token_db.find_one({ "token": token }))

    return fsapi.listing(token.tenant, path)

@xtoken_required
@api_api.route("/v1/error")
def api_error():
    return json_result(-1, "error")