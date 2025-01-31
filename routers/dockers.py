import uuid, json

from flask import Flask, url_for, request, session, render_template, redirect, Blueprint
from flask_pymongo import PyMongo, wrappers
from flask_uuid import FlaskUUID

from classes.api.dockerimage import DockerImageAPI
from classes.api.dockercontainer import DockerContainerAPI
from classes.daemon.dockerdaemon import DockerDaemon

from models.image import Image
from models.container import Container
from models.dockerfile import Dockerfile
from database import mongo
from util import deserialize_json, login_required, randomString, error, json_result
from daemons import docker_daemon

docker_api = Blueprint("docker_api", __name__)
docker_daemon.start()

@docker_api.route("/docker", methods=["GET"])
@docker_api.route("/docker/list", methods=["GET"])
@login_required
def docker_list():
    uid: uuid.UUID = session.get("uuid")
    db: wrappers.Collection = mongo.db.images
    images: list = deserialize_json(Image, db.find({ "uid": uid }))

    db: wrappers.Collection = mongo.db.containers
    containers: list = deserialize_json(Container, db.find({ "uid": uid }))

    return render_template("docker/list.html", images=images, containers=containers)

@docker_api.route("/docker/images", methods=["GET"])
@login_required
def docker_images():
    uid: uuid.UUID = session.get("uuid")
    db: wrappers.Collection = mongo.db.images
    result: list = deserialize_json(Image, db.find({ "uid": uid }))

    return render_template("docker/images.html", images=result)

@docker_api.route("/docker/images/search", methods=["POST"])
@login_required
def docker_images_search():
    tag = request.form["tag"]
    uid = session.get("uuid")
    db: wrappers.Collection = mongo.db.images
    result: list = deserialize_json(Image, db.find({ "uid": uid, "tag": { "$regex": tag } }))
    r = []
    for image in result:
        r += [ image.__dict__ ]
    return json_result(0, r)

@docker_api.route("/docker/containers", methods=["GET"])
@login_required
def docker_containers():
    uid = session.get("uuid")
    db: wrappers.Collection = mongo.db.containers
    result: list = deserialize_json(Container, db.find({ "uid": uid }))

    return render_template("docker/containers.html", containers=result)

@docker_api.route("/docker/containers/search", methods=["POST"])
@login_required
def docker_containers_search():
    tag = request.form["tag"]
    uid = session.get("uuid")
    db: wrappers.Collection = mongo.db.containers
    result: list = deserialize_json(Container, db.find({ "uid": uid, "tag": { "$regex": tag } }))
    r = []
    for container in result:
        r += [ container.__dict__ ]

    return json_result(0, result)

@docker_api.route("/docker/<uuid:sid>/status")
@login_required
def docker_status(sid: uuid.UUID, methods=["GET"]):
    """
    :param sid: docker uuid
    """
    db: wrappers.Collection = mongo.db.containers
    result: Container = deserialize_json(Container, db.find_one({ "uuid": str(sid) }))
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
        return json_result(-1, "POST only")
    
    uid = session.get("uuid")
    username = session.get("username")
    tag = request.form["tag"]
    dockfile = request.form["dockfile"]
    rootpass = request.form["rootpass"]
    sshport = int(request.form["sshport"])

    fn = "upload/{}/{}/Dockerfile".format(username, dockfile)
    with open(fn, "r") as f:
        df = f.read()

    name = tag.split(":")[0]
    ver = "latest"
    if len(tag.split(":")) == 1:
        ver = tag.split(":")[1]
    tag = randomString(20 - len(name)) + name + ":" + ver
    
    image_uuid = str(uuid.uuid4())
    container_uuid = str(uuid.uuid4())

    image = Image(uid, "", tag, "installing", sshport, "", image_uuid)
    db: wrappers.Collection = mongo.db.images
    db.insert_one(image.__dict__)

    # search Dockerfile
    df: wrappers.Collection = mongo.db.dockerfile
    result: Dockerfile = deserialize_json(Dockerfile, df.find_one({ "uuid": dockfile }))
    if result == None:
        return json_result(-1, "Dockerfile is not exist")

    try:
        # image build
        image.status = "build"
        db.update({ "uuid": image_uuid }, image.__dict__)
        result, imgs = DockerImageAPI.build(result.path, rootpass, tag)
        image.short_id = imgs[0]["Id"].split(":")[1]
        print(result)

        image.status = "done"
        db.update({ "uuid": image_uuid }, image.__dict__)
    except:
        image.status = "fail"
        db.update({ "uuid": image_uuid }, image.__dict__)
        return json_result(-1, "Dockerfile::Image::build fail")

    # container start
    container_id = DockerImageAPI.run(tag, "", sshport) # image.run(tag, port=sshport)
    container = Container(uid, tag, "start", image_uuid, sshport, container_id, container_uuid)
    container.start(container_id)
    db: wrappers.Collection = mongo.db.containers
    db.insert_one(container.__dict__)

    docker_daemon.notify(container_id)

    result_stream = []
    for item in result:
        try:
            result_stream += [item["stream"]]
        except:
            continue

    return json_result(0, "".join(result_stream))

@docker_api.route("/docker/run/<uuid:sid>", methods=["POST"])
@login_required
def docker_run(sid: uuid.UUID):
    if request.method != "POST":
        return json_result(-1, "POST only")

    sid = str(sid)
    tag = request.form["tag"]
    sshport = int(request.form["sshport"])
    uid = session.get("uuid")

    db: wrappers.Collection = mongo.db.images
    image: Image = deserialize_json(Image, db.find_one({ "uid": uid, "uuid": sid }))
    if not image:
        return json_result(-1, "Docker::Images::rmi failed")
    
    container_id = DockerImageAPI.run(tag, "", sshport) # image.run(tag, port=sshport)
    container_uuid = str(uuid.uuid4())
    container = Container(uid, tag, "start", sid, sshport, container_id, container_uuid)
    db: wrappers.Collection = mongo.db.containers
    db.insert_one(container.__dict__)

    DockerContainerAPI.start(container)
    docker_daemon.notify(container_id)

    return json_result(0, "Successfully run")


@docker_api.route("/docker/rmi/<uuid:sid>", methods=["GET"])
@login_required
def docker_rmi(sid: uuid.UUID):
    """
    :param uid: user uuid
    :param sid: image uuid
    """
    sid = str(sid)
    uid: uuid.UUID = session.get("uuid")
    db: wrappers.Collection = mongo.db.images
    image: Image = deserialize_json(Image, db.find_one({ "uid": uid, "uuid": sid }))
    if not image:
        return json_result(-1, "Docker::Images::rmi failed")

    ct: wrappers.Collection = mongo.db.containers
    containers: list = deserialize_json(Container, ct.find({ "image": sid }))
    for item in containers:
        container: Container = item
        status = docker_status(container.uuid)
        if status != "stop":
            return json_result(-1, "Docker::Images::rmi failed(container is alive)")

    # delete image
    DockerImageAPI.delete(image.tag)
    return json_result(0, "Successfully image removed")

@docker_api.route("/docker/start/<uuid:sid>", methods=["GET"])
@login_required
def docker_start(sid: uuid.UUID):
    sid = str(sid)
    uid = session.get("uuid")
    db: wrappers.Collection = mongo.db.containers
    container: Container = deserialize_json(Container, db.find_one({ "uid": uid, "uuid": sid }))
    if not container:
        return json_result(-1, "container not found")

    # container start & check
    try:
        DockerContainerAPI.start(container)
        return json_result(0, "container start")
    except:
        container.status = "failed"
        db.update({ "uid": uid, "uuid": sid }, container.__dict__)

    return json_result(-1, "Docker::Container::start failed")

@docker_api.route("/docker/stop/<uuid:sid>", methods=["GET"])
@login_required
def docker_stop(sid: uuid.UUID):
    sid = str(sid)
    uid = session.get("uuid")
    db: wrappers.Collection = mongo.db.containers
    container: Container = deserialize_json(Container, db.find_one({ "uid": uid, "uuid": sid }))
    if not container:
        return json_result(-1, "container not found")

    # container stop & check
    try:
        DockerContainerAPI.stop(container)
    except:
        return json_result(-1, "Docker::Container::stop failed")

    return json_result(0, "container stop")

@docker_api.route("/docker/rm/<uuid:sid>", methods=["GET"])
@login_required
def docker_rm(sid: uuid.UUID):
    sid = str(sid)
    uid = session.get("uuid")
    db: wrappers.Collection = mongo.db.containers
    container: Container = deserialize_json(Container, db.find_one({ "uid": uid, "uuid": sid }))
    if not container:
        return render_template("fail.html")

    status = container.status
    container.status = "removing"
    db.update({ "uid": uid, "uuid": sid }, container.__dict__)

    try:
        DockerContainerAPI.remove(container)
        docker_daemon.notify_remove(container.short_id)
    except:
        container.status = status
        db.update({ "uid": uid, "uuid": sid }, container.__dict__)
        return json_result(-1, "Docker::Container::remove failed")

    return json_result(0, "Successfully container removed")