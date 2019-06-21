from dockerengine import client

class DockerContainerAPI(object):
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