from classes.api.api import API
from classes.api.dockerimage import DockerImageAPI
from classes.api.dockercontainer import DockerContainerAPI

class DockerAPI(API):
    def __init__(self):
        self.image = DockerImageAPI()
        self.container = DockerContainerAPI()
    
    def logging(self):
        pass