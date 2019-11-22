#!/bin/sh

apt-get update
apt-get upgrade
curl -fsSL https://get.docker.com/ | sh
apt-get install python3 python3-pip
pip3 install -r requirements.txt
