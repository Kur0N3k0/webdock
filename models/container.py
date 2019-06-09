from dockerengine import client
import docker, uuid

class Container(object):
    def __init__(self, uid: uuid.UUID, tag: str, status: str, image: uuid.UUID, short_id, uuid: uuid.UUID):
        self.uid = uid
        self.tag = tag
        self.status = status
        self.image = image
        self.short_id = short_id
        self.uuid = uuid
    
    def getContainers(self):
        return client.containers()

    def start(self, container_id):
        client.start(container=container_id)
        return True
    
    def stop(self, container_id):
        container: docker.models.containers.Container = client.containers.get(container_id)
        container.stop()
        return True

    def delete(self, container_id):
        container: docker.models.containers.Container = client.containers.get(container_id)
        container.remove()
        return True
    
    def is_stopped(self, container_id):
        return True