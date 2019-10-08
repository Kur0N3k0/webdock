import requests

def auth(uid, upw):
    url = "http://192.168.0.13:3000/api/v1/request_auth"
    return requests.post(url, data={"username": uid, "password": upw}).json()

def getImages(token):
    url = "http://192.168.0.13:3000/api/v1/images"
    return requests.get(url, headers={"X-Access-Token": token}).json()

token = auth("asdf", "asdf")["msg"]["token"]
print(getImages(token))