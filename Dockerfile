FROM kylemanna/openvpn

MAINTAINER Mesosphere <team@mesosphere.com>

RUN apk -U add ca-certificates python py-setuptools

COPY . /dcos

WORKDIR /dcos
RUN ["/usr/bin/python", "setup.py", "install"]
EXPOSE 5000 1194/tcp 1194/udp
ENTRYPOINT ["/dcos/bin/run.bash" ]
CMD [ "server"]
