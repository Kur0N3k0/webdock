from dockerengine import client
import docker, uuid, json, io

class Image(json.JSONEncoder):
    def __init__(self,
                uid: uuid.UUID = "",
                os: str = "",
                tag: str = "",
                status: str = "",
                port:int = 0,
                short_id: str = "",
                _uuid: uuid.UUID = ""
    ):
        self.uid = uid
        self.os = os
        self.tag = tag
        self.port = port
        self.status = status
        self.short_id = short_id
        self.uuid = _uuid