import requests

def auth(uid, upw):
    url = "http://nekop.kr:3000/api/v1/request_auth"
    return requests.post(url, data={"username": uid, "password": upw}).json()

def getImages(token):
    url = "http://nekop.kr:3000/api/v1/images"
    return requests.get(url, headers={"X-Access-Token": token}).json()

def getContainers(token):
    url = "http://nekop.kr:3000/api/v1/containers"
    return requests.get(url, headers={"X-Access-Token": token}).json()

def runImage(token):
    url = "http://nekop.kr:3000/api/v1/image/run/02dcd458-bb7e-48eb-84e4-8d72d8ad706f/7777"
    return requests.get(url, headers={"X-Access-Token": token}).json()

def stopContainer(token):
    url = "http://nekop.kr:3000/api/v1/container/stop/2b3d6c78-644c-45e7-a5f8-f9ef0bcc7267"
    return requests.get(url, headers={"X-Access-Token": token}).json()

def startContainer(token):
    url = "http://nekop.kr:3000/api/v1/container/start/2b3d6c78-644c-45e7-a5f8-f9ef0bcc7267"
    return requests.get(url, headers={"X-Access-Token": token}).json()
token = auth("kuroneko", "nekoplus")["msg"]["token"]
print(token)
print(getImages(token))
print(getContainers(token))
#print(runImage(token))
#print(stopContainer(token))
print(startContainer(token))
