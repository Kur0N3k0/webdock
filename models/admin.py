from models.user import User
import uuid

class Admin(User):
    def __init__(self, username: str, password: str, level: int, _uuid: uuid.UUID):
        super(username, password, level, _uuid)

    def add_user(self):
        pass

    def delete_user(self):
        pass

    def update_user(self):
        pass
    
    def assign_image2user(self):
        pass
    
    def unassign_image2user(self):
        pass

    def assign_container2user(self):
        pass
    
    def unassign_container2user(self):
        pass

    def remove_image(self):
        pass

    def remove_container(self):
        pass

    def remove_dockerfile(self):
        pass