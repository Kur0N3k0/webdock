import uuid

from flask import Flask, url_for, request, session, render_template, redirect, Blueprint
from flask_pymongo import PyMongo, wrappers
from flask_uuid import FlaskUUID

from classes.payment.coupon import Coupon
from models.docker_collection import DockerCollection
from models.image import Image
from models.container import Container
from models.user import User

from database import mongo
from util import deserialize_json, admin_required, json_result

admin_api = Blueprint("admin_api", __name__)
docker_api = DockerCollection()

@admin_api.route("/admin")
@admin_required
def admin_index():
    return render_template("/admin/index.html")

@admin_api.route("/admin/images")
@admin_required
def admin_images():
    images = docker_api.image.getImages()
    return render_template("/admin/image.html", images=images)

@admin_api.route("/admin/images/remove/<uuid:sid>")
@admin_required
def admin_images_remove(sid: uuid.UUID):
    db: wrappers.Collection = mongo.db.images
    image: Image = deserialize_json(Image, db.find_one({ "uuid": sid }))
    docker_api.image.delete(image.tag)
    db.delete_one({ "uuid": str(sid) })
    return json_result(0, "success")

@admin_api.route("/admin/containers")
@admin_required
def admin_containers():
    containers = docker_api.container.getContainers()
    return render_template("/admin/container.html", containers=containers)

@admin_api.route("/admin/containers/remove/<uuid:sid>")
@admin_required
def admin_containers_remove(sid: uuid.UUID):
    db: wrappers.Collection = mongo.db.containers
    container: Container = deserialize_json(Container, db.find_one({ "uuid": sid }))
    docker_api.container.remove(container.short_id)
    db.delete_one({ "uuid": str(sid) })
    return json_result(0, "success")

@admin_api.route("/admin/users")
@admin_required
def admin_users():
    db: wrappers.Collection = mongo.db.users
    users: list = deserialize_json(User, db.find())
    return render_template("/admin/user.html", users=users)

@admin_api.route("/admin/users/add", methods=["GET", "POST"])
@admin_required
def admin_users_add():
    if request.method == "GET":
        return render_template("/admin/user-add.html")
    
    username = request.form["username"]
    password = request.form["pasword"]
    level = request.form["level"]
    sid = uuid.uuid4()
    user = User(username, password, level, sid)
    
    db: wrappers.Collection = mongo.db.users
    db.insert_one(user.__dict__)

    return json_result(0, "success")

@admin_api.route("/admin/users/remove/<uuid:sid>")
@admin_required
def admin_users_remove(sid: uuid.UUID):
    db: wrappers.Collection = mongo.db.users
    db.delete_one({ "uuid": str(sid) })
    return json_result(0, "success")

@admin_api.route("/admin/users/setlevel/<uuid:sid>/<int:level>")
@admin_required
def admin_users_setlevel(sid: uuid.UUID, level: int):
    if level != 0 and level != 1:
        return json_result(-1, "invalid level")

    db: wrappers.Collection = mongo.db.users
    user: User = deserialize_json(User, db.find_one({ "uuid": str(sid) }))
    user.level = level

    db.update_one({ "uuid": str(sid) }, user.__dict__)
    return json_result(0, "success")

@admin_api.route("/admin/coupon/give")
@admin_required
def admin_coupon_give():
    user = request.form["user"]
    cp = Coupon()
    if cp.give(user, cp.generate()):
        return json_result(0, "success")
    return json_result(-1, "coupon give fail")
