from flask_uuid import FlaskUUID

class Docker(object):
    uid = ""
    os = ""
    tag = ""
    ver = ""
    status = ""
    uuid = ""

    def __init__(self, uid: uuid, os: str, tag: str, ver: str, status: str, uuid: uuid):
        self.uid = uid
        self.os = os
        self.tag = tag
        self.ver = ver
        self.status = status
        self.uuid = uuid

    def build(self):
        return ""

    def run(self):
        return ""
    
    def start(self):
        return ""
    
    def stop(self):
        return ""

    def delete(self):
        return ""

    def is_stopped(self):
        return True