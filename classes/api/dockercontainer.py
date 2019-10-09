from dockerengine import client
from flask_pymongo import PyMongo, wrappers
from database import mongo
from util import deserialize_json

from models.container import Container

class DockerContainerAPI(object):
    @staticmethod
    def getContainers():
        return client.containers()

    @staticmethod
    def start(container_id):
        client.start(container=container_id)
        db: wrappers.Collection = mongo.db.containers
        db.update({ "short_id": container_id }, { "status": "start" })
        return True
    
    @staticmethod
    def stop(container_id):
        client.stop(container=container_id)
        db: wrappers.Collection = mongo.db.containers
        db.update({ "short_id": container_id }, { "status": "stop" })
        return True

    @staticmethod
    def remove(container_id):
        client.remove_container(container=container_id)
        db: wrappers.Collection = mongo.db.containers
        db.delete_one({ "short_id": container_id })
        return True
    
    @staticmethod
    def is_stopped(container_id):
        return True
    
    @staticmethod
    def status(container_id):
        return client.containers(filters={"id": container_id})
    
    def find_by_shortid(self, short_id):
        db: wrappers.Collection = mongo.db.containers
        return deserialize_json(Container, db.find_one({ "short_id": short_id }))
