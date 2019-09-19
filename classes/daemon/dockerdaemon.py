from flask_pymongo import PyMongo, wrappers
from classes.daemon.daemon import Daemon
from classes.api.docker import DockerContainerAPI
from models.container import Container
from database import mongo
from util import deserialize_json, login_required, randomString, error, json_result

import threading

class DockerDaemon(Daemon):
    def __init__(self):
        super()
        self.running = False
        self.thread = None
        for container in DockerContainerAPI.getContainers():
            self.queue += [container["Id"][:12]]
    
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=docker_worker, args=(self, ))
        self.thread.start()
    
    def stop(self):
        self.running = False
        self.thread.join()
    
    def notify(self, container_id):
        self.queue += [container_id]
        return True

def docker_worker(daemon: DockerDaemon):
    while daemon.running:
        if len(daemon.queue) < 0:
            continue

        for container_id in daemon.queue:
            container = DockerContainerAPI.status(container_id)
            if container["Id"][:12] == container_id:
                db: wrappers.Collection = mongo.db.containers
                result: Container = deserialize_json(Container, db.find_one({ "short_id": container_id }))
                if result.status == "start" and container["State"] == "stopped":
                    result.status = "stop"
                    db.update({ "short_id": container_id }, result.__dict__)
            break