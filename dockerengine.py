import docker

client = docker.APIClient(base_url='unix://var/run/docker.sock')