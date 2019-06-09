FROM            ubuntu:16.04
MAINTAINER      kuroneko@nekop.kr
WORKDIR         /

RUN apt-get update
RUN apt-get -y install openssh-server curl wget vim
RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/g' /etc/ssh/sshd_config