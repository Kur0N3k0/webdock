from flask_uuid import FlaskUUID
import docker

class Dockers(object):
    uid = ""
    os = ""
    tag = ""
    ver = ""
    status = ""
    uuid = ""
    client = docker.from_env()

    def __init__(self, uid: uuid, os: str, tag: str, ver: str, status: str, uuid: uuid):
        self.uid = uid
        self.os = os
        self.tag = tag
        self.ver = ver
        self.status = status
        self.uuid = uuid

    def build(self, path):
        image: docker.models.images.Image = self.client.build(path, tag=self.tag)
        return image.labels

    def run(self, image, command=None):
        container: docker.models.containers.Container = self.client.containers.run(image, command=command)
        return container
    
    def start(self, container_id):
        container: docker.models.containers.Container = self.client.containers.get(container_id)
        container.start()
        return True
    
    def stop(self, container_id):
        container: docker.models.containers.Container = self.client.containers.get(container_id)
        container.stop()
        return True

    def delete(self, container_id):
        container: docker.models.containers.Container = self.client.containers.get(container_id)
        container.remove()
        return True

    def delete_image(self, label):
        self.client.images.remove(image=label)
        return True
    
    def is_stopped(self, container_id):
        return True