import uuid

from flask import Flask, url_for, request, session, render_template, redirect, Blueprint
from flask_pymongo import PyMongo, wrappers
from flask_uuid import FlaskUUID

from models.image import Image
from models.container import Container
from models.dockerfile import Dockerfile
from database import mongo

docker_api = Blueprint("docker_api", __name__)

login_check = lambda: session.get("username") != None

@docker_api.route("/docker")
@docker_api.route("/docker/list")
def docker_list():
    if login_check() == False:
        return render_template("fail.html")
    
    uid: uuid.UUID = session.get("uuid")
    db: wrappers.Collection = mongo.db.images
    images: list = db.find({ "uid": uid })
    if not images:
        return render_template("fail.html")

    db: wrappers.Collection = mongo.db.containers
    containers: list = db.find({ "uid": uid })
    if not containers:
        return render_template("fail.html")

    return render_template("docker/list.html", images=images, containers=containers)

@docker_api.route("/docker/images")
def docker_images():
    if login_check() == False:
        return render_template("fail.html")

    uid: uuid.UUID = session.get("uuid")
    db: wrappers.Collection = mongo.db.images
    result: list = db.find({ "uid": uid })
    if not result:
        return render_template("fail.html")
    return render_template("docker/containers.html", containers=result)

@docker_api.route("/docker/containers")
def docker_containers():
    if login_check() == False:
        return render_template("fail.html")

    uid: uuid.UUID = session.get("uuid")
    db: wrappers.Collection = mongo.db.containers
    result: list = db.find({ "uid": uid })
    if not result:
        return render_template("fail.html")
    return render_template("docker/containers.html", containers=result)

@docker_api.route("/docker/<uuid:sid>/status")
def docker_status(sid: uuid.UUID, methods=["GET"]):
    """
    :param sid: docker uuid
    """
    if login_check() == False:
        return render_template("fail.html")
    
    db: wrappers.Collection = mongo.db.containers
    result: Container = db.find_one({ "uuid": sid })
    if result == None:
        return render_template("fail.html")

    return result.status

@docker_api.route("/docker/build", methods=["POST"])
def docker_build(uid: uuid.UUID):
    """
    GET
    :param uid: user uuid

    POST
    :param tag: docker tag
    :param ver: container version
    :parma dockfile: dockerfile uuid

    build Dockerfile
    """
    if login_check() == False:
        return render_template("fail.html")

    if request.method != "POST":
        return ""
    
    uid: uuid.UUID = session.get("uuid")
    tag = request.form["tag"]
    ver = request.form["ver"]
    dockfile = request.form["dockfile"]
    image_uuid = uuid.uuid4()
    container_uuid = uuid.uuid4()

    image = Image(uid, "", tag, ver, "installing", image_uuid)
    db: wrappers.Collection = mongo.db.images
    db.insert_one(image.__dict__)

    # search Dockerfile
    df: wrappers.Collection = mongo.db.dockerfile
    result: Dockerfile = df.find_one({ "uuid": dockfile })
    if result == None:
        render_template("fail.html")

    # image build
    image.status = "build"
    db.update_one({ "uuid": image_uuid }, image.__dict__)
    short_id = image.build(result.path)

    image.status = "done"
    db.update_one({ "uuid": image_uuid }, image.__dict__)

    # container start
    container_info = image.run(short_id)
    container = Container(uid, tag, ver, "start", image_uuid, container_info.short_id, container_uuid)
    db: wrappers.Collection = mongo.db.containers
    db.insert_one(container.__dict__)

    return ""

@docker_api.route("/docker/rmi/<uuid:sid>")
def docker_rmi(sid: uuid.UUID, methods=["POST"]):
    """
    :param uid: user uuid
    :param sid: image uuid
    """
    if login_check() == False:
        return render_template("fail.html")

    uid: uuid.UUID = session.get("uuid")
    db: wrappers.Collection = mongo.db.images
    image: Image = db.find_one({ "uid": uid, "uuid": sid })
    if image == None:
        return render_template("fail.html")

    ct: wrappers.Collection = mongo.db.containers
    containers = ct.find({ "image": sid })
    for item in containers:
        container: Container = item
        status = docker_status(container.uuid)
        if status != "stop":
            return render_template("fail.html")

    image.status = "uninstalling"
    db.update_one({ "uuid": sid }, image.__dict__)

    # delete image
    image.delete()

    db.delete_one({ "uuid": sid })

    return ""

@docker_api.route("/docker/start/<uuid:sid>")
def docker_start(sid: uuid.UUID, methods=["GET"]):
    if login_check() == False:
        return render_template("fail.html")
    
    uid: uuid.UUID = session.get("uuid")
    db: wrappers.Collection = mongo.db.containers
    container: Container = db.find_one({ "uid": uid, "uuid": sid })
    if container == None:
        return render_template("fail.html")
    
    container.status = "run"
    db.update_one({ "uid": uid, "uuid": sid }, container.__dict__)

    # container start & check
    try:
        container.start()

        container.status = "start"
        db.update_one({ "uid": uid, "uuid": sid }, container.__dict__)
        return "start"
    except:
        container.status = "failed"
        db.update_one({ "uid": uid, "uuid": sid }, container.__dict__)
        return "failed"

@docker_api.route("/docker/stop/<uuid:sid>")
def docker_stop(sid: uuid.UUID, methods=["GET"]):
    if login_check() == False:
        return render_template("fail.html")
    
    uid: uuid.UUID = session.get("uuid")
    db: wrappers.Collection = mongo.db.docker
    container: Container = db.find_one({ "uid": uid, "uuid": sid })
    if container == None:
        return render_template("fail.html")
    
    container.status = "stopping"
    db.update_one({ "uid": uid, "uuid": sid }, container)

    # container stop & check
    try:
        container.stop()

        container.status = "stop"
        db.update_one({ "uid": uid, "uuid": sid }, container)
        return "stop"
    except:
        container.status = "failed"
        db.update_one({ "uid": uid, "uuid": sid }, container)
        return "failed"

    return "stop"