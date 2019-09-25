import uuid

from flask import Flask, url_for, request, session, render_template, redirect, Blueprint
from flask_pymongo import PyMongo, wrappers
from flask_uuid import FlaskUUID

from classes.user.user import Users
from classes.payment.coupon import Coupon
from models.docker_collection import DockerCollection
from models.image import Image
from models.container import Container
from models.dockerfile import Dockerfile
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
    image: Image = deserialize_json(Image, db.find_one({ "uuid": str(sid) }))
    docker_api.image.delete(image.tag)
    db.delete_one({ "uuid": str(sid) })
    return json_result(0, "success")

# not necessary
@admin_api.route("/admin/images/build/<uuid:sid>", methods=["POST"])
@admin_required
def admin_images_build(sid: uuid.UUID):
    user: User = Users.find_by_name(session["username"])
    rootpass = request.form["rootpass"]
    tag = request.form["tag"]
    uid = user.uuid
    image_uuid = str(uuid.uuid4())

    image: Image = Image(uid, "", tag, "installing", 0, image_uuid)
    db: wrappers.Collection = mongo.db.images
    db.insert_one(image.__dict__)

    db2: wrappers.Collection = mongo.db.dockerfile
    dockerfile: Dockerfile = deserialize_json(Dockerfile, db2.find_one({ "uuid": str(sid) }))
    if dockerfile == None:
        return json_result(-1, "dockerfile not exist")

    try:
        image.status = "build"
        db.update({ "uuid": image_uuid }, image.__dict__)
        docker_api.image.build(dockerfile.path, rootpass, tag)
    except:
        pass

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

@admin_api.route("/admin/users/update/<uuid:sid>", methods=["POST"])
@admin_required
def admin_users_update(sid: uuid.UUID):
    password = request.form["password"]
    level = request.form["level"]
    
    user: User = Users.find_by_uuid(str(sid))
    if user == None:
        return json_result(-1, "user not found")
    
    user.password = password
    try:
        user.level = int(level)
    except:
        return json_result(-1, "level is not integer")
    if user.level not in [0, 1]:
        return json_result(-1, "invalid level")

    db: wrappers.Collection = mongo.db.users
    db.update({ "uuid": str(sid) }, user.__dict__)
    return json_result(0, "success")

@admin_api.route("/admin/users/setlevel/<uuid:sid>/<int:level>")
@admin_required
def admin_users_setlevel(sid: uuid.UUID, level: int):
    if level not in [0, 1]:
        return json_result(-1, "invalid level")

    db: wrappers.Collection = mongo.db.users
    user: User = deserialize_json(User, db.find_one({ "uuid": str(sid) }))
    user.level = level

    db.update_one({ "uuid": str(sid) }, user.__dict__)
    return json_result(0, "success")

@admin_api.route("/admin/coupon/give", methods=["POST"])
@admin_required
def admin_coupon_give():
    user = request.form["user"]
    cp = Coupon()
    if cp.give(user, cp.generate()):
        return json_result(0, "success")
    return json_result(-1, "coupon give fail")

@admin_api.route("/admin/coupon/remove", methods=["POST"])
@admin_required
def admin_coupon_remove():
    username = request.form["user"]
    coupon = request.form["coupon"]
    cp = Coupon()
    if cp.remove(username, coupon):
        return json_result(0, "success")
    return json_result(-1, "coupon remove fail")

