from flask_uuid import FlaskUUID
import docker

class Dockers(object):
    client = docker.from_env()

    def __init__(self, uid: uuid, os: str, tag: str, ver: str, status: str, uuid: uuid):
        self.uid = uid
        self.os = os
        self.tag = tag
        self.ver = ver
        self.status = status
        self.label = { "uid": uid }
        self.uuid = uuid

    def getImages(self):
        images = self.client.images.list(filters={ "label": self.label })
        return images

    def getContainers(self):
        containers = self.client.containers.list(filters={ "label": self.label })
        return containers

    def build(self, path):
        image: docker.models.images.Image = self.client.build(path, tag=self.tag, labels=self.label)
        return image.labels

    def run(self, image_id, command=None):
        container: docker.models.containers.Container = self.client.containers.run(image_id, command=command, labels=self.label)
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

    def delete_image(self, image_id):
        self.client.images.remove(image=image_id)
        return True
    
    def is_stopped(self, container_id):
        return True