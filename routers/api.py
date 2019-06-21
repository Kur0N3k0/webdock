import uuid

from flask import Flask, url_for, request, session, render_template, redirect, Blueprint
from flask_pymongo import PyMongo, wrappers
from flask_uuid import FlaskUUID

from models.image import Image
from models.container import Container

api_api = Blueprint("api_api", __name__, url_prefix="/api")

@api_api.route("/v1/request_auth")
def api_request_auth():
    pass

@api_api.route("/v1/images")
def api_images():
    pass

@api_api.route("/v1/containers")
def api_containers():
    pass

@api_api.route("/v1/image/rm")
def api_image_rm():
    pass

@api_api.route("/v1/container/rm")
def api_container_rm():
    pass

@api_api.route("/v1/image/<uuid:sid>")
def api_image_detail(sid: uuid.UUID):
    pass

@api_api.route("/v1/container/<uuid:sid>")
def api_container_detail(sid: uuid.UUID):
    pass

@api_api.route("/v1/image/run/<uuid:sid>")
def api_image_run(sid: uuid.UUID):
    pass

@api_api.route("/v1/container/start/<uuid:sid>")
def api_container_start(sid: uuid.UUID):
    pass

@api_api.route("/v1/container/stop/<uuid:sid>")
def api_container_stop(sid: uuid.UUID):
    pass

