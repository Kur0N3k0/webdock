import uuid, json

from flask import Flask, url_for, request, session, render_template, redirect, Blueprint
from flask_pymongo import PyMongo, wrappers
from flask_uuid import FlaskUUID

from models.image import Image
from models.container import Container
from models.dockerfile import Dockerfile
from database import mongo
from util import deserialize_json, login_required, randomString, error

docker_api = Blueprint("docker_api", __name__)

@docker_api.route("/docker")
@docker_api.route("/docker/list")
@login_required
def docker_list():
    uid: uuid.UUID = session.get("uuid")
    db: wrappers.Collection = mongo.db.images
    images: list = deserialize_json(Image, db.find({ "uid": uid }))

    db: wrappers.Collection = mongo.db.containers
    containers: list = deserialize_json(Container, db.find({ "uid": uid }))

    return render_template("docker/list.html", images=images, containers=containers)

@docker_api.route("/docker/images")
@login_required
def docker_images():
    uid: uuid.UUID = session.get("uuid")
    db: wrappers.Collection = mongo.db.images
    result: list = deserialize_json(Image, db.find({ "uid": uid }))

    return render_template("docker/images.html", images=result)

@docker_api.route("/docker/containers")
@login_required
def docker_containers():
    uid: uuid.UUID = session.get("uuid")
    db: wrappers.Collection = mongo.db.containers
    result: list = deserialize_json(Container, db.find({ "uid": uid }))
    
    return render_template("docker/containers.html", containers=result)

@docker_api.route("/docker/<uuid:sid>/status")
@login_required
def docker_status(sid: uuid.UUID, methods=["GET"]):
    """
    :param sid: docker uuid
    """
    db: wrappers.Collection = mongo.db.containers
    result: Container = deserialize_json(Container, db.find_one({ "uuid": sid }))
    if result == None:
        return "failed"

    return result.status

@docker_api.route("/docker/build", methods=["POST"])
@login_required
def docker_build():
    """
    GET
    :param uid: user uuid

    POST
    :param tag: docker tag
    :parma dockfile: dockerfile uuid
    :param rootpass: root password for ssh
    :param sshport: ssh port forwarding

    build Dockerfile
    """
    if request.method != "POST":
        return "failed"
    
    uid = session.get("uuid")
    tag = request.form["tag"]
    dockfile = request.form["dockfile"]
    rootpass = request.form["rootpass"]
    sshport = int(request.form["sshport"])

    fn = "upload/{}/{}/Dockerfile".format(uid, dockfile)
    with open(fn, "r") as f:
        df = f.read()

    name = tag.split(":")[0]
    ver = tag.split(":")[1]
    tag = randomString(20 - len(name)) + name + ":" + ver
    
    image_uuid = str(uuid.uuid4())
    container_uuid = uuid.uuid4()

    image = Image(uid, "", tag, "installing", image_uuid)
    db: wrappers.Collection = mongo.db.images
    db.insert_one(image.__dict__)

    # search Dockerfile
    df: wrappers.Collection = mongo.db.dockerfile
    result: Dockerfile = deserialize_json(Dockerfile, df.find_one({ "uuid": dockfile }))
    if result == None:
        return "failed"

    #try:
        # image build
    image.status = "build"
    db.update({ "uuid": image_uuid }, image.__dict__)
    result, imgs = image.build(result.path, rootpass)

    image.status = "done"
    db.update({ "uuid": image_uuid }, image.__dict__)
    #except:
    #    image.status = "done"
    #    db.update({ "uuid": image_uuid }, image.__dict__)
    #    return error("Dockerfile::Image::build fail")

    # container start
    container_id = image.run(tag, port=sshport)
    container = Container(uid, tag, "start", image_uuid, container_id, container_uuid)
    container.start(container_id)
    db: wrappers.Collection = mongo.db.containers
    db.insert_one(container.__dict__)

    return json.dumps(result)

@docker_api.route("/docker/rmi/<uuid:sid>")
@login_required
def docker_rmi(sid: uuid.UUID, methods=["POST"]):
    """
    :param uid: user uuid
    :param sid: image uuid
    """
    uid: uuid.UUID = session.get("uuid")
    db: wrappers.Collection = mongo.db.images
    image: Image = deserialize_json(Image, db.find_one({ "uid": uid, "uuid": sid }))
    if image == None:
        return "failed"

    ct: wrappers.Collection = mongo.db.containers
    containers: list = deserialize_json(Container, ct.find({ "image": sid }))
    for item in containers:
        container: Container = item
        status = docker_status(container.uuid)
        if status != "stop":
            return "failed"

    image.status = "uninstalling"
    db.update_one({ "uuid": sid }, image.__dict__)

    # delete image
    image.delete()

    db.delete_one({ "uuid": sid })

    return "success"

@docker_api.route("/docker/start/<uuid:sid>")
@login_required
def docker_start(sid: uuid.UUID, methods=["GET"]):
    uid: uuid.UUID = session.get("uuid")
    db: wrappers.Collection = mongo.db.containers
    container: Container = deserialize_json(Container, db.find_one({ "uid": uid, "uuid": sid }))
    if container == None:
        return "failed"
    
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
@login_required
def docker_stop(sid: uuid.UUID, methods=["GET"]):
    uid: uuid.UUID = session.get("uuid")
    db: wrappers.Collection = mongo.db.docker
    container: Container = deserialize_json(Container, db.find_one({ "uid": uid, "uuid": sid }))
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