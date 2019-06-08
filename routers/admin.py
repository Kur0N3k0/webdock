import uuid

from flask import Flask, url_for, request, session, render_template, redirect, Blueprint
from flask_pymongo import PyMongo, wrappers
from flask_uuid import FlaskUUID

from models.image import Image
from models.container import Container
from models.dockerfile import Dockerfile
from database import mongo
from util import deserialize_json

admin_api = Blueprint("admin_api", __name__)

@admin_api.route("/admin")
def admin_index():
    return ""

@admin_api.route("/admin/images")
def admin_images():
    return ""

@admin_api.route("/admin/images/remove/<uuid:sid>")
def admin_images_remove(sid: uuid.UUID):
    return ""

@admin_api.route("/admin/containers")
def admin_containers():
    return ""

@admin_api.route("/admin/containers/remove/<uuid:sid>")
def admin_containers_remove(sid: uuid.UUID):
    return ""

@admin_api.route("/admin/users")
def admin_users():
    return ""

@admin_api.route("/admin/users/remove/<uuid:sid>")
def admin_users_remove(sid: uuid.UUID):
    return ""

@admin_api.route("/admin/users/manage/<uuid:sid>")
def admin_users_manage(sid: uuid.UUID):
    return ""