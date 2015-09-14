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

setup-dns:
	echo 'DOCKER_OPTS="-b=bridge0"' >> /etc/default/docker
