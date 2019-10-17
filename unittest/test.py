import requests

def auth(uid, upw):
    url = "http://nekop.kr:3000/api/v1/request_auth"
    return requests.post(url, data={"username": uid, "password": upw}).json()

def getImages(token):
    url = "http://nekop.kr:3000/api/v1/images"
    return requests.get(url, headers={"X-Access-Token": token}).json()

token = auth("test", "test")["msg"]["token"]
print(token)
print(getImages(token))
