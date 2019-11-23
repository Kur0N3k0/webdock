#!/bin/sh

apt-get update
apt-get upgrade
curl -fsSL https://get.docker.com/ | sh
wget -qO - https://www.mongodb.org/static/pgp/server-4.2.asc | apt-key add -
echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.2 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-4.2.list
apt-get update
apt-get install python3 python3-pip mongodb-org
pip3 install -r requirements.txt
