DCOS OpenVPN
===============

How does it work?
--------------

1. Take `marathon.json` and POST it to marathon.
1. Marathon launches the dcos-openvpn scheduler on a private agent.
1. The scheduler docker container comes up and `bin/run.bash` is called.
1. Zookeeper is checked to see if the config has been uploaded or not yet.
1. If there is nothing in zookeeper, the configuration is built (via. ovpn_genconfig) and then uploaded to zookeeper.
1. If there is already state in zookeeper, the configuration is downloaded from there and placed into the scheduler's docker container.
1. At this point, the actual dcos-openvpn scheduler is started. It registers with mesos and waits for resource offers.
1. Once the scheduler receives a resource offer that is from a slave_public with 256mb of memory and 0.1 cpus, it launches the actual openvpn server on a public slave.
1. The openvpn task launches in the same docker as the scheduler (see Dockerfile) and runs the beginning bash script.
1. The configuration is downloaded from zk that was previously uploaded by the scheduler on first startup.
1. The script goes out externally and fetches its remote ip.
1. The openvpn server starts running. At this point, the openvpn server is running, but there are no user profiles.
1. Now, you'll need to create a user profile. To do that, POST `name=myname` to scheduler_ip:scheduler_port/client.
1. The client will be generated (by calling easyrsa build-client-full) and then uploaded via. zkcli.
1. Once the cert is uploaded, the full output will be returned to you via. the POST body.

Development
------------

- Make sure you're running a slave with the `slave_public` role.
- Run `make dev`. This will run the scheduler in a docker and assumes that `leader.mesos` is resolvable. If you want to change the master location, alter MESOS_CONFIG.
- Openvpn server runs in a docker in bridge mode. Because of this, you'll need to have mesos-dns running locally and add `--dns <host-ip>` to `/etc/default/docker`.

```
echo "DOCKER_OPTS=\"--dns $(ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}')\"" >> /etc/default/docker
sudo restart docker

sudo docker run --net=host -d -v data/config.json:/config.json mesosphere/mesos-dns /mesos-dns -config=/config.json
```
