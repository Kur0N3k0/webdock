from dockerengine import client
from flask_pymongo import PyMongo, wrappers
from database import mongo
from util import deserialize_json

from models.image import Image

import json, io

class DockerImageAPI(object):
    @staticmethod
    def getImages():
        return client.images()

    @staticmethod
    def build(path, rootpass, tag):
        df = open(path, "r").read()
        df += """
RUN apt-get update
RUN apt-get -y install openssh-server
RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/g' /etc/ssh/sshd_config
RUN echo "root:{}" | chpasswd
CMD echo 0 > /proc/sys/kernel/yama/ptrace_scope
CMD /etc/init.d/ssh start && /bin/bash -c "while true; do echo 'still alive'; sleep 600; done"
""".format(rootpass)
        f = io.BytesIO(df.encode())
        build_result = client.build(fileobj=f, tag=tag, rm=True)
        result = [ json.loads(line) for line in build_result ]
        imgs = client.images(name=tag.split(":")[0])

        return result, imgs

    @staticmethod
    def run(image_tag, command, port):
        return client.create_container(
            image=image_tag,
            command=command,
            ports=[22],
            host_config=client.create_host_config(
                port_bindings={ 22: port }
            )
        )['Id']

    @staticmethod
    def delete(image_id):
        client.remove_image(image_id)
        db: wrappers.Collection = mongo.db.images
        db.delete_one({ "tag": image_id })
        return True
    
    def find_by_tag(self, tag):
        db: wrappers.Collection = mongo.db.images
        image: Image = deserialize_json(Image, db.find_one({ "tag": tag }))
        return image