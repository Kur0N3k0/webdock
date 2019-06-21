from dockerengine import client
import json, io

class DockerImageAPI(object):
    def getImages(self):
        return client.images()

    def build(self, path, rootpass, tag=""):
        if tag != "":
            self.tag = tag

        df = open(path, "r").read()
        df += """
RUN apt-get -y install openssh-server
RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/g' /etc/ssh/sshd_config
RUN echo "root:{}" | chpasswd
CMD echo 0 > /proc/sys/kernel/yama/ptrace_scope
CMD /etc/init.d/ssh start && /bin/bash -c "while true; do echo 'still alive'; sleep 600; done"
""".format(rootpass)
        f = io.BytesIO(df.encode())
        build_result = client.build(fileobj=f, tag=self.tag, rm=True)
        result = [ json.loads(line) for line in build_result ]
        imgs = client.images(name=self.tag.split(":")[0])

        return result, imgs

    def run(self, image_tag, command=None, port=0):
        if port != 0:
            self.port = port

        return client.create_container(
            image=image_tag,
            command=command,
            ports=[22],
            host_config=client.create_host_config(
                port_bindings={ 22: self.port }
            )
        )['Id']

    def delete(self, image_id):
        client.remove_image(image_id)
        return True