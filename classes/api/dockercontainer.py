from dockerengine import client

class DockerContainerAPI(object):
    @staticmethod
    def getContainers():
        return client.containers()

    @staticmethod
    def start(container_id):
        client.start(container=container_id)
        return True
    
    @staticmethod
    def stop(container_id):
        client.stop(container=container_id)
        return True

    @staticmethod
    def remove(container_id):
        client.remove_container(container=container_id)
        return True
    
    @staticmethod
    def is_stopped(container_id):
        return True