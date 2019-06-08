import uuid

from flask import Flask, url_for, request, session, render_template, redirect, Blueprint
from flask_pymongo import PyMongo, wrappers
from flask_uuid import FlaskUUID

from models.dockers import Dockers
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
    db: wrappers.Collection = mongo.db.docker
    result: list = db.find({ "uid": uid })
    if not result:
        return render_template("fail.html")

    return render_template("docker/list.html", docker=result)

@docker_api.route("/docker/images")
def docker_images():
    return redirect("/docker/list")

@docker_api.route("/docker/containers")
def docker_containers():
    if login_check() == False:
        return render_template("fail.html")
        

@docker_api.route("/docker/<uuid:sid>/status")
def docker_status(sid: uuid.UUID, methods=["GET"]):
    """
    :param sid: docker uuid
    """
    if login_check() == False:
        return render_template("fail.html")
    
    db: wrappers.Collection = mongo.db.docker
    result: Dockers = db.find_one({ "uuid": sid })
    if result == None:
        return render_template("fail.html")

    return result.status

@docker_api.route("/docker/install", methods=["POST"])
def docker_install(uid: uuid.UUID):
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
    vm_uuid = uuid.uuid4()

    docker = Dockers(uid, "", tag, ver, "installing", vm_uuid)
    db: wrappers.Collection = mongo.db.docker
    db.insert_one(docker.__dict__)

    # search Dockerfile
    df: wrappers.Collection = mongo.db.dockerfile
    result: Dockerfile = df.find_one({ "uuid": dockfile })
    if result == None:
        render_template("fail.html")

    # docker build
    docker.status = "build"
    db.update_one({ "uuid": vm_uuid }, docker)
    label = docker.build(result.path)

    # docker start
    docker.status = "start"
    db.update_one({ "uuid": vm_uuid }, docker)
    docker.run(label)

    return ""

@docker_api.route("/docker/uninstall/<uuid:sid>")
def docker_uninstall(sid: uuid.UUID, methods=["POST"]):
    """
    :param uid: user uuid
    :param sid: docker uuid
    """
    if login_check() == False:
        return render_template("fail.html")

    uid: uuid.UUID = session.get("uuid")
    db: wrappers.Collection = mongo.db.docker
    docker: Dockers = db.find_one({ "uid": uid, "uuid": sid })
    if docker == None:
        return render_template("fail.html")

    st = docker_status(sid)
    if st != "stop":
        return render_template("fail.html")

    docker.status = "uninstalling"
    db.update_one({ "uuid": sid }, docker)

    # delete docker
    docker.delete()

    db.delete_one({ "uuid": sid })

    return ""

@docker_api.route("/docker/start/<uuid:sid>")
def docker_start(sid: uuid.UUID, methods=["GET"]):
    if login_check() == False:
        return render_template("fail.html")
    
    uid: uuid.UUID = session.get("uuid")
    db: wrappers.Collection = mongo.db.docker
    docker: Dockers = db.find_one({ "uid": uid, "uuid": sid })
    if docker == None:
        return render_template("fail.html")
    
    docker.status = "run"
    db.update_one({ "uid": uid, "uuid": sid }, docker)

    # docker start & check
    docker.start()

    docker.status = "start"
    db.update_one({ "uid": uid, "uuid": sid }, docker)

    return "start"

@docker_api.route("/docker/stop/<uuid:sid>")
def docker_stop(sid: uuid.UUID, methods=["GET"]):
    if login_check() == False:
        return render_template("fail.html")
    
    uid: uuid.UUID = session.get("uuid")
    db: wrappers.Collection = mongo.db.docker
    docker: Dockers = db.find_one({ "uid": uid, "uuid": sid })
    if docker == None:
        return render_template("fail.html")
    
    docker.status = "stopping"
    db.update_one({ "uid": uid, "uuid": sid }, docker)

    # docker stop & check
    docker.stop()
    while not docker.is_stopped():
        continue

    docker.status = "stop"
    db.update_one({ "uid": uid, "uuid": sid }, docker)

    return "stop"