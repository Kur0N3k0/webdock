from dockerengine import client
import docker, uuid, json, io

class Image(object):
    def __init__(self, uid: uuid.UUID, os: str, tag: str, status: str, _uuid: uuid.UUID):
        self.uid = uid
        self.os = os
        self.tag = tag
        self.status = status
        self.label = { "uid": uid, "uuid": _uuid }
        self.uuid = _uuid

    def getImages(self):
        return client.images()

    def build(self, path, rootpass):
        df = open(path, "r").read()
        df += """
RUN apt-get -y install openssh-server
RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/g' /etc/ssh/sshd_config
RUN echo "root:{}" | chpasswd
CMD echo 0 > /proc/sys/kernel/yama/ptrace_scope
CMD /etc/init.d/ssh start && /bin/bash -c "while true; do echo 'still alive'; sleep 600; done"
""".format(rootpass)
        f = io.BytesIO(df.encode())
        result = [ json.loads(line) for line in client.build(fileobj=f, tag=self.tag) ]
        imgs = client.images(name=self.tag.split(":")[0])
        return result, imgs

    def run(self, image_tag, command=None, port=9505):
        return client.create_container(
            image=image_tag,
            command=command,
            ports=[22],
            host_config=client.create_host_config(
                port_bindings={ 22: port }
            )
        )['Id']

    def delete(self, image_id):
        client.remove_image(image_id)
        return True