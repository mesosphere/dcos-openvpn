FROM kylemanna/openvpn
ENV MESOS_EGG mesos-0.24.1-py2.7-linux-x86_64.egg

MAINTAINER Mesosphere <team@mesosphere.com>

RUN apk -U add python py-setuptools && apk -U -t deps add curl ca-certificates \
    && curl -Lo $MESOS_EGG https://downloads.mesosphere.io/master/ubuntu/15.04/$MESOS_EGG \
    && easy_install-2.7 $MESOS_EGG && rm $MESOS_EGG && apk del deps

COPY . /dcos

WORKDIR /dcos
RUN ["/usr/bin/python",  "setup.py", "install"]

CMD ["/dcos/bin/run.bash", "server"]
