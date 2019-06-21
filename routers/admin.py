import uuid

from flask import Flask, url_for, request, session, render_template, redirect, Blueprint
from flask_pymongo import PyMongo, wrappers
from flask_uuid import FlaskUUID

from models.docker_collection import DockerCollection

from database import mongo
from util import deserialize_json, admin_required

admin_api = Blueprint("admin_api", __name__)
docker_api = DockerCollection()

@admin_api.route("/admin")
@admin_required
def admin_index():
    return ""

@admin_api.route("/admin/images")
@admin_required
def admin_images():
    images = docker_api.image.getImages()
    return ""

@admin_api.route("/admin/images/remove/<uuid:sid>")
@admin_required
def admin_images_remove(sid: uuid.UUID):
    db: wrappers.Collection = mongo.db.images

    db.find_one({})

    return ""

@admin_api.route("/admin/containers")
@admin_required
def admin_containers():
    return ""

@admin_api.route("/admin/containers/remove/<uuid:sid>")
@admin_required
def admin_containers_remove(sid: uuid.UUID):
    return ""

@admin_api.route("/admin/users")
@admin_required
def admin_users():
    return ""

@admin_api.route("/admin/users/remove/<uuid:sid>")
@admin_required
def admin_users_remove(sid: uuid.UUID):
    return ""

@admin_api.route("/admin/users/manage/<uuid:sid>")
@admin_required
def admin_users_manage(sid: uuid.UUID):
    return ""