from flask_uuid import FlaskUUID
import uuid

class Dockerfile(object):
    def __init__(self, uid: uuid, name: str, path: str, date: int, _uuid: uuid.UUID):
        self.uid = uid
        self.path = path
        self.name = name
        self.date = date
        self.uuid = _uuid