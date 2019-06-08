import logging
import uuid
import os
from flask import Flask, url_for, request, session, render_template, redirect
from flask_pymongo import PyMongo, wrappers
from flask_uuid import FlaskUUID
from werkzeug.utils import secure_filename

from models.user import User
from models.image import Image
from models.container import Container
from models.dockerfile import Dockerfile

from database import mongo
from dockerengine import docker

log = logging.Logger("webdock")

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/webdock"
mongo.init_app(app)
m_uuid = FlaskUUID()
m_uuid.init_app(app)

from routers.user import user_api
from routers.dockers import docker_api
from routers.dockerfile import dockerfile_api
from routers.payment import payment_api

app.register_blueprint(user_api)
app.register_blueprint(docker_api)
app.register_blueprint(dockerfile_api)
app.register_blueprint(payment_api)

@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(host="0.0.0.0", port="3000", debug=True)