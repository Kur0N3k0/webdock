from dockerengine import client
import docker, uuid

class Image(object):
    def __init__(self, uid: uuid.UUID, os: str, tag: str, ver: str, status: str, uuid: uuid.UUID):
        self.uid = uid
        self.os = os
        self.tag = tag
        self.ver = ver
        self.status = status
        self.label = { "uid": uid }
        self.uuid = uuid

    def getImages(self):
        return client.images.list(filters={ "label": self.label })

    def build(self, path):
        image: docker.models.images.Image = client.build(path, tag=self.tag, labels=self.label)
        return image.short_id

    def run(self, image_id, command=None):
        container: docker.models.containers.Container = client.containers.run(image_id, command=command, labels=self.label)
        return container
    
    def start(self, container_id):
        container: docker.models.containers.Container = client.containers.get(container_id)
        container.start()
        return True
    
    def stop(self, container_id):
        container: docker.models.containers.Container = client.containers.get(container_id)
        container.stop()
        return True

    def delete(self, container_id):
        container: docker.models.containers.Container = client.containers.get(container_id)
        container.remove()
        return True

    def delete_image(self, image_id):
        client.images.remove(image=image_id)
        return True
    
    def is_stopped(self, container_id):
        return True