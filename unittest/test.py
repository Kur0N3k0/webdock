import requests

def auth(uid, upw):
    url = "http://192.168.0.13:3000/api/v1/request_auth"
    return requests.post(url, data={"tenant": uid, "password": upw}).text

print(auth("b30d1e92-e356-4aca-8c3c-c20b7bf7dc76", "asdf"))