from dockerengine import client
import docker, uuid

class Container(object):
    def __init__(self, uid: uuid.UUID, tag: str, ver: str, status: str, image: uuid.UUID, short_id, uuid: uuid.UUID):
        self.uid = uid
        self.tag = tag
        self.ver = ver
        self.status = status
        self.label = { "uid": uid }
        self.image = image
        self.short_id = short_id
        self.uuid = uuid
    
    def getContainers(self):
        return client.containers.list(filters={ "label": self.label })

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
    
    def is_stopped(self, container_id):
        return True