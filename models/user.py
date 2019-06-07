from flask_uuid import FlaskUUID

class User(object):
    name = ""
    password = ""
    uuid = ""

    def __init__(self, name: str, password: str, uuid: uuid):
        self.name = name
        self.password = password
        self.uuid = uuid