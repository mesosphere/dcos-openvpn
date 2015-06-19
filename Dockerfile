FROM kylemanna/openvpn

MAINTAINER Mesosphere <team@mesosphere.com>

RUN apt-get update && \
    apt-get install -y curl wget libsvn1 python2.7-minimal python-setuptools && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN wget http://downloads.mesosphere.io/master/ubuntu/14.04/mesos-0.22.0-py2.7-linux-x86_64.egg && \
    easy_install mesos-0.22.0-py2.7-linux-x86_64.egg

COPY . /dcos

WORKDIR /dcos
RUN ["/usr/bin/python",  "setup.py", "install"]

CMD ["/dcos/bin/run.bash", "server"]
