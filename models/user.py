from models.payment import Payment
import uuid

class User(object):
    def __init__(self, username: str, password: str, level: int, _uuid: uuid.UUID):
        self.username = username
        self.password = password
        self.level = level
        self.uuid = _uuid
    
    def add_image(self):
        pass
    
    def remove_image(self):
        pass
    
    def add_container(self):
        pass
    
    def remove_container(self):
        pass
    
    def add_dockerfile(self):
        pass
    
    def remove_dockerfile(self):
        pass