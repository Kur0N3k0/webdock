from flask_uuid import FlaskUUID
import uuid

class Dockerfile(object):
    def __init__(self, uid: uuid, path: str, date: int, _uuid: uuid.UUID):
        self.uid = uid
        self.path = path
        self.date = date
        self.uuid = _uuid