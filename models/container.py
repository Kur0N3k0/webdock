from dockerengine import client
import docker, uuid, time

class Container(object):
    def __init__(self,
                uid: uuid.UUID = "",
                tag: str = "",
                status: str = "",
                image: uuid.UUID = "",
                port: int = 0,
                short_id = "",
                uuid: uuid.UUID = ""
    ):
        self.uid = uid
        self.tag = tag
        self.status = status
        self.image = image
        self.port = port
        self.short_id = short_id
        self.started_time = time.time()
        self.uuid = uuid
    
    def getContainers(self):
        return client.containers()

    def start(self, container_id):
        client.start(container=container_id)
        return True
    
    def stop(self, container_id):
        client.stop(container=container_id)
        return True

    def remove(self, container_id):
        client.remove_container(container=container_id)
        return True
    
    def is_stopped(self, container_id):
        return True