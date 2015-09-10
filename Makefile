all: env test packages

clean:
	bin/clean.sh

env:
	bin/env.sh

test:
	bin/test.sh

packages:
	bin/packages.sh

push:
	bin/push.sh

dev:
	docker run								\
	-it									\
	--net=host								\
	-v /vagrant/dcos-openvpn:/dcos						\
	thomasr/dcos-openvpn							\
	/dcos/bin/test.sh
