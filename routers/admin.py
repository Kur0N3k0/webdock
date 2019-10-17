import uuid

from flask import Flask, url_for, request, session, render_template, redirect, Blueprint
from flask_pymongo import PyMongo, wrappers
from flask_uuid import FlaskUUID

from classes.user.user import Users as user_api
from classes.payment.coupon import Coupon
from classes.api.docker import DockerAPI
from models.image import Image
from models.container import Container
from models.dockerfile import Dockerfile
from models.user import User

from database import mongo
from util import deserialize_json, admin_required, json_result

admin_api = Blueprint("admin_api", __name__)
coupon_api = Coupon()
docker_api = DockerAPI()

@admin_api.route("/admin")
@admin_required
def admin_index():
    return render_template("/admin/index.html")

@admin_api.route("/admin/images")
@admin_required
def admin_images():
    images = docker_api.image.getImages()
    result = []
    for image in images:
        rimage = Image()
        rimage.uid = "system"
        rimage.uuid = "system"
        rimage.status = "done"
        rimage.tag = image["RepoTags"][0]

        r: Image = docker_api.image.find_by_tag(rimage.tag)
        if r != None:
            rimage.uid = r.uid
            rimage.uuid = r.uuid
            rimage.status = r.status
        u: User = user_api.find_by_uuid(rimage.uid)
        if u != None:
            rimage.uid = u.username
        
        rimage.tag = rimage.tag.replace(":", "-")
        result += [rimage]
    
    return render_template("/admin/image.html", images=result)

@admin_api.route("/admin/images/run", methods=["POST"])
@admin_required
def admin_images_run():
    tag = request.form["tag"]
    idx = tag.rfind("-")
    tag = tag[:idx] + ":" + tag[idx + 1:]
    docker_api.image.run(tag, "", 22)
    return json_result(0, "success")


@admin_api.route("/admin/images/remove/<tag>")
@admin_required
def admin_images_remove(tag: str):
    idx = tag.rfind("-")
    tag = tag[:idx] + ":" + tag[idx + 1:]
    image: Image = docker_api.image.find_by_tag(tag)
    if image == None:
        return json_result(-1, "image not exists")
    
    docker_api.image.delete(image.tag)
    return json_result(0, "success")

@admin_api.route("/admin/containers")
@admin_required
def admin_containers():
    containers = docker_api.container.getContainers()
    result = []
    for container in containers:
        rcontainer: Container = Container()
        rcontainer.uid = "system"
        rcontainer.uuid = "system"
        rcontainer.short_id = container["Id"]
        rcontainer.tag = container["Image"]
        rcontainer.status = container["State"]
        r: Container = docker_api.container.find_by_shortid(rcontainer.short_id)
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
    return json_result(0, "success")

@admin_api.route("/admin/containers/stop/<short_id>")
@admin_required
def admin_containers_stop(short_id):
    docker_api.container.stop(short_id)
    return json_result(0, "success")

@admin_api.route("/admin/containers/remove/<short_id>")
@admin_required
def admin_containers_remove(short_id):
    docker_api.container.remove(short_id)
    return json_result(0, "success")

@admin_api.route("/admin/users")
@admin_required
def admin_users():
    return render_template("/admin/user.html", users=user_api.all())

@admin_api.route("/admin/users/add", methods=["POST"])
@admin_required
def admin_users_add():
    username = request.form["username"]
    password = request.form["password"]
    level = int(request.form["level"])

    if "../" in username:
        return json_result(0, "invalid username")

    result = user_api.find_by_name(username)
    if result != None:
        return json_result(-1, "exist user")

    u_uuid = user_api.add(username, password, level)

    return json_result(0, u_uuid)

@admin_api.route("/admin/users/remove/<uuid:sid>")
@admin_required
def admin_users_remove(sid: uuid.UUID):
    if str(sid) == "b30d1e92-e356-4aca-8c3c-c20b7bf7dc76":
        return json_result(-1, "master admin can't remove")
    user_api.remove_by_uuid(sid)
    return json_result(0, "success")

@admin_api.route("/admin/users/update/<uuid:sid>", methods=["POST"])
@admin_required
def admin_users_update(sid: uuid.UUID):
    password = request.form["password"]
    level = request.form["level"]
    
    user: User = user_api.find_by_uuid(sid)
    if user == None:
        return json_result(-1, "user not found")
    
    user.password = password
    try:
        user.level = int(level)
    except:
        return json_result(-1, "level is not integer")
    if user.level not in User.LEVELS:
        return json_result(-1, "invalid level")

    user_api.update_by_uuid(sid, user)
    return json_result(0, "success")

@admin_api.route("/admin/users/setlevel/<uuid:sid>/<int:level>")
@admin_required
def admin_users_setlevel(sid: uuid.UUID, level: int):
    if level not in User.LEVELS:
        return json_result(-1, "invalid level")

    user: User = user_api.find_by_uuid(sid)
    user.level = level
    user_api.update_by_uuid(sid, user)
    return json_result(0, "success")

@admin_api.route("/admin/coupon", methods=["GET"])
@admin_required
def admin_coupon():
    return render_template("/admin/coupon.html", coupons=coupon_api.all())

@admin_api.route("/admin/coupon/give", methods=["POST"])
@admin_required
def admin_coupon_give():
    user = request.form["username"]
    cp = Coupon()
    if coupon_api.give(user, cp.generate()):
        return json_result(0, "success")
    return json_result(-1, "coupon give fail")

@admin_api.route("/admin/coupon/remove", methods=["POST"])
@admin_required
def admin_coupon_remove():
    username = request.form["username"]
    coupon = request.form["coupon"]
    if coupon_api.remove(username, coupon):
        return json_result(0, "success")
    return json_result(-1, "coupon remove fail")

