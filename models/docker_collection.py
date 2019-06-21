from models.image import Image
from models.container import Container
from models.dockerfile import Dockerfile

class DockerCollection(object):
    def __init__(self):
        self.image = Image()
        self.container = Container()
        self.dockerfile = Dockerfile()