from flask_uuid import FlaskUUID
import uuid

class Dockerfile(object):
    def __init__(self,
                uid: uuid.UUID = "",
                name: str = "",
                path: str = "",
                date: int = 0,
                _uuid: uuid.UUID = ""
    ):
        self.uid = uid
        self.path = path
        self.name = name
        self.date = date
        self.uuid = _uuid