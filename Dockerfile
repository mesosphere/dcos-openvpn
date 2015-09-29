FROM kylemanna/openvpn
ENV MESOS_EGG mesos-0.24.1-py2.7-linux-x86_64.egg

MAINTAINER Mesosphere <team@mesosphere.com>

RUN apt-get update && \
    apt-get install -y curl wget libsvn1 python2.7-minimal python-setuptools && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN wget http://downloads.mesosphere.io/master/ubuntu/15.04/$MESOS_EGG \
    && easy_install $MESOS_EGG && rm $MESOS_EGG

COPY . /dcos

WORKDIR /dcos
RUN ["/usr/bin/python",  "setup.py", "install"]

CMD ["/dcos/bin/run.bash", "server"]
