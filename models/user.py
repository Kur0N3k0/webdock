import uuid

class User(object):
    def __init__(self, username: str, password: str, level: int, _uuid: uuid.UUID):
        self.username = username
        self.password = password
        self.level = level
        self.uuid = str(_uuid)