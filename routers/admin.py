import uuid

from flask import Flask, url_for, request, session, render_template, redirect, Blueprint
from flask_pymongo import PyMongo, wrappers
from flask_uuid import FlaskUUID

from classes.user.user import Users
from classes.payment.coupon import Coupon
from classes.api.docker import DockerAPI
from models.image import Image
from models.container import Container
from models.dockerfile import Dockerfile
from models.user import User

from database import mongo
from util import deserialize_json, admin_required, json_result

admin_api = Blueprint("admin_api", __name__)
docker_api = DockerAPI()

@admin_api.route("/admin")
@admin_required
def admin_index():
    return render_template("/admin/index.html")

@admin_api.route("/admin/images")
@admin_required
def admin_images():
    db: wrappers.Collection = mongo.db.images
    udb: wrappers.Collection = mongo.db.users
    images = docker_api.image.getImages()
    result = []
    for image in images:
        rimage = Image()
        rimage.uid = "system"
        rimage.uuid = "system"
        rimage.status = "done"
        rimage.tag = image["RepoTags"][0]

        r: Image = deserialize_json(Image, db.find_one({ "tag": rimage.tag }))
        if r != None:
            rimage.uid = r.uid
            rimage.uuid = r.uuid
            rimage.status = r.status
        u: User = deserialize_json(User, udb.find_one({ "uid": rimage.uid }))
        if u != None:
            rimage.uid = u.username
        
        rimage.tag = rimage.tag.replace(":", "-")
        result += [rimage]
    
    return render_template("/admin/image.html", images=result)

@admin_api.route("/admin/images/remove/<tag>")
@admin_required
def admin_images_remove(tag: str):
    idx = tag.rfind("-")
    tag = tag[:idx] + ":" + tag[idx + 1:]
    db: wrappers.Collection = mongo.db.images
    image: Image = deserialize_json(Image, db.find_one({ "tag": tag }))
    if image == None:
        return json_result(-1, "image not exists")
    
    docker_api.image.delete(image.tag)
    db.delete_one({ "tag": tag })
    return json_result(0, "success")

@admin_api.route("/admin/containers")
@admin_required
def admin_containers():
    containers = docker_api.container.getContainers()
    db: wrappers.Collection = mongo.db.containers

    result = []
    for container in containers:
        rcontainer: Container = Container()
        rcontainer.uid = "system"
        rcontainer.uuid = "system"
        rcontainer.short_id = container["Id"]
        rcontainer.tag = container["Image"]
        rcontainer.status = container["State"]
        r: Container = deserialize_json(Container, db.find_one({ "short_id": rcontainer.short_id }))
        if r != None:
            rcontainer.uid = r.uid
            rcontainer.uuid = r.uuid
            rcontainer.status = r.status
        result += [rcontainer]

    return render_template("/admin/container.html", containers=result)

@admin_api.route("/admin/containers/start/<short_id>")
@admin_required
def admin_containers_start(short_id):
    docker_api.container.start(short_id)
    db: wrappers.Collection = mongo.db.containers
    db.update({ "short_id": short_id }, { "status": "start" })
    return json_result(0, "success")

@admin_api.route("/admin/containers/stop/<short_id>")
@admin_required
def admin_containers_stop(short_id):
    docker_api.container.stop(short_id)
    db: wrappers.Collection = mongo.db.containers
    db.update({ "short_id": short_id }, { "status": "stop" })
    return json_result(0, "success")

@admin_api.route("/admin/containers/remove/<short_id>")
@admin_required
def admin_containers_remove(short_id):
    docker_api.container.remove(short_id)
    db: wrappers.Collection = mongo.db.containers
    db.delete_one({ "short_id": short_id })
    return json_result(0, "success")

@admin_api.route("/admin/users")
@admin_required
def admin_users():
    db: wrappers.Collection = mongo.db.users
    users: list = deserialize_json(User, db.find())
    return render_template("/admin/user.html", users=users)

@admin_api.route("/admin/users/add", methods=["POST"])
@admin_required
def admin_users_add():
    username = request.form["username"]
    password = request.form["password"]
    level = int(request.form["level"])

    if "../" in username:
        return json_result(0, "invalid username")

    db: wrappers.Collection = mongo.db.users
    result = db.find_one({ "username": username })
    if result != None:
        return json_result(-1, "exist user")

    u_uuid = uuid.uuid4()
    user = User(username, password, level, u_uuid)
    db.insert_one(user.__dict__)

    return json_result(0, str(u_uuid))

@admin_api.route("/admin/users/remove/<uuid:sid>")
@admin_required
def admin_users_remove(sid: uuid.UUID):
    if str(sid) == "b30d1e92-e356-4aca-8c3c-c20b7bf7dc76":
        return json_result(-1, "master admin can't remove")
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
    if user.level not in User.LEVELS:
        return json_result(-1, "invalid level")

    db: wrappers.Collection = mongo.db.users
    db.update({ "uuid": str(sid) }, user.__dict__)
    return json_result(0, "success")

@admin_api.route("/admin/users/setlevel/<uuid:sid>/<int:level>")
@admin_required
def admin_users_setlevel(sid: uuid.UUID, level: int):
    if level not in User.LEVELS:
        return json_result(-1, "invalid level")

    db: wrappers.Collection = mongo.db.users
    user: User = deserialize_json(User, db.find_one({ "uuid": str(sid) }))
    user.level = level

    db.update_one({ "uuid": str(sid) }, user.__dict__)
    return json_result(0, "success")

@admin_api.route("/admin/coupon", methods=["GET"])
@admin_required
def admin_coupon():
    return render_template("/admin/coupon.html")

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

