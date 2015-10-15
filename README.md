DCOS OpenVPN
===============

How does it work?
--------------

### Deploy Admin
1. Take `marathon-admin.json` and POST it to marathon.
1. Marathon launches the admin web interface on a private agent.
1. The docker container comes up and `bin/run.bash` is called.
1. Zookeeper is checked to see if the config has been uploaded or not yet.
1. If there is nothing in zookeeper, the configuration is built (via. ovpn_genconfig) and then uploaded to zookeeper.
1. If there is already state in zookeeper, the configuration is downloaded from there and placed into the scheduler's docker container.

### Deploy Server
1. Take `marathon-server.json` and POST it to marathon.
1. Marathon launches the openvpn server on a public agent.
1. The configuration is downloaded from zk that was previously uploaded by the scheduler on first startup.
1. The script goes out externally and fetches its remote ip.
1. The openvpn server starts running. At this point, the openvpn server is running, but there are no user profiles.


### Add Users
1. Now, you'll need to create a user profile. To do that, POST `name=myname` to admin_ip:scheduler_port/client.
1. The client will be generated (by calling easyrsa build-client-full) and then uploaded via zkcli.
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
