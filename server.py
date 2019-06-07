import logging
import uuid
import os
from flask import Flask, url_for, request, session, render_template, redirect
from flask_pymongo import PyMongo, wrappers
from flask_uuid import FlaskUUID
from werkzeug.utils import secure_filename

from models.user import User
from models.dockers import Dockers
from models.dockerfile import Dockerfile

log = logging.Logger("webdock")

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/webdock"
mongo = PyMongo(app)
m_uuid = FlaskUUID()
m_uuid.init_app(app)

def login_check():
    return session.get("username") != None

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

#
# User route
#
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if login_check() == True:
        return ""

    if request.method == "GET":
        return render_template("user/signup.html")

    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db: wrappers.Collection = mongo.db.users
        result = db.find_one({ "username": username })
        if result != None:
            return "exist user"

        u_uuid = uuid.uuid4()
        user = User(username, password, u_uuid)
        db.insert_one(user.__dict__)

        session["username"] = username
        session["uuid"] = u_uuid

    return redirect("/docker")

@app.route("/signin", methods=["GET", "POST"])
def signin():
    """
    POST
    :param username: username
    :param password: password
    """
    if request.method == "GET":
        return render_template("user/signin.html")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db: wrappers.Collection = mongo.db.users
        result: User = db.find_one({ "username": username, "password": password })
        if result == None:
            return ""

        session["username"] = username
        session["uuid"] = result.uuid

    return redirect("/docker")

@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return index()

#
# Dockers route
#
@app.route("/docker")
@app.route("/docker/list")
def docker_list():
    if login_check() == False:
        return ""
    
    uid: uuid.UUID = session.get("uuid")
    db: wrappers.Collection = mongo.db.docker
    result: Dockers = db.find({ "uid": uid })
    if result == None:
        return ""

    return render_template("docker/list.html", docker=result)

@app.route("/docker/<uuid:sid>/status")
def docker_status(sid: uuid.UUID, methods=["GET"]):
    """
    :param sid: docker uuid
    """
    if login_check() == False:
        return ""
    
    db: wrappers.Collection = mongo.db.docker
    result: Dockers = db.find_one({ "uuid": sid })
    if result == None:
        return ""

    return result.status

@app.route("/docker/install", methods=["POST"])
def docker_install(uid: uuid.UUID):
    """
    GET
    :param uid: user uuid

    POST
    :param tag: docker tag
    :param ver: container version
    :parma dockfile: dockerfile uuid
    """
    if login_check() == False:
        return render_template("fail.html")

    if request.method != "POST":
        return ""
    
    uid: uuid.UUID = session.get("uuid")
    tag = str(uid) + "_" + request.form["tag"]
    ver = request.form["ver"]
    dockfile = request.form["dockfile"]
    vm_uuid = uuid.uuid4()

    docker = Dockers(uid, "", tag, ver, "installing", vm_uuid)
    db: wrappers.Collection = mongo.db.docker
    db.insert_one(docker)

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

@app.route("/docker/uninstall/<uuid:sid>")
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

@app.route("/docker/start/<uuid:sid>")
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

@app.route("/docker/stop/<uuid:sid>")
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

@app.route("/docker/images")
def docker_images():
    return ""

#
# Dockersfile route
#
@app.route("/dockerfile")
@app.route("/dockerfile/list")
def dockerfile():
    if login_check() == False:
        return render_template("fail.html")

    db: wrappers.Collection = mongo.db.dockerfile
    uid: uuid.UUID = session.get("uuid")

    result: Dockerfile = db.find({ "uuid": uid })

    return render_template("docker/list.html")

@app.route("/dockerfile/upload", methods=["POST"])
def dockerfile_upload():
    if login_check() == False:
        return render_template("fail.html")

    f = request.files["file"]
    fn = "/upload/" + secure_filename(f.filename)
    f.save(fn)

    uid = session.get("uuid")
    fn_uuid = uuid.uuid4()
    db: wrappers.Collection = mongo.db.dockerfile
    db.insert_one(Dockerfile(uid, fn, fn_uuid).__dict__)
    
    return ""

@app.route("/dockerfile/view/<uuid:fn_uuid>")
def dockerfile_view(fn_uuid: uuid.UUID):
    if login_check() == False:
        return render_template("fail.html")

    db: wrappers.Collection = mongo.db.dockerfile
    uid = session.get("uuid")
    result: Dockersfile = db.find_one({ "uid": uid, "uuid": fn_uuid })
    if result == None:
        return render_template("fail.html")

    with open(result.path, "rb") as f:
        df = f.read()

    return ""

@app.route("/dockerfile/save")
def dockerfile_save():

    return ""

#
# Payment route
#
@app.route("/payment")
def payment():
    return render_template("payment/index.html")

#
# 
#

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(host="0.0.0.0", port="3000", debug=True)