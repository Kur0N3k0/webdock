from flask_uuid import FlaskUUID

class Dockerfile(object):
    uid = ""
    uuid = ""

    def __init__(self, uid: uuid, path: str, uuid: uuid):
        self.uid = uid
        self.path = path
        self.uuid = uuid