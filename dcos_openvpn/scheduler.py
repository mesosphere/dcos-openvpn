
from __future__ import absolute_import, print_function

import logging
import os
import threading
from Queue import Queue
import uuid

from mesos.interface import Scheduler
from mesos.interface import mesos_pb2
from mesos.native import MesosSchedulerDriver as SchedulerDriver

import dcos_openvpn
from . import util



class VPNScheduler(Scheduler):

    name = "openvpn"
    version = dcos_openvpn.__version__

    role = "public_slave"
    resources = {
        "mem": 10,
        "cpus": 0.1
    }

    def __init__(self):
        self.running = False

    def run(self):
        t = threading.Thread(target=self.driver.run)
        t.setDaemon(True)
        t.start()

    @property
    @util.memoize
    def driver(self):
        fwinfo = mesos_pb2.FrameworkInfo(
            user="",
            name=self.name,
            role="public_slave",
            checkpoint=True,
            webui_url="http://{0}:{1}/".format(
                os.environ["MESOS_HOSTNAME"],
                os.environ["PORT0"])
        )
        return SchedulerDriver(
            self,
            fwinfo,
            os.environ.get("MESOS_CONFIG", "zk://leader.mesos:2181/mesos")
        )

    def registered(self, driver, fwid, minfo):
        logging.info("registered: id={0}".format(fwid.value))

    def set_resource(self, a, x):
        if x.type == 0: # scalar
            a[x.name] = x.scalar.value
        elif x.type == 1: # range
            a[x.name] = [(y.begin, y.end) for y in x.ranges.range]
        return a

    def convert_offer(self, offer):
        return (offer, reduce(self.set_resource,
            [r for r in offer.resources if r.role == self.role], {}))

    def resourceOffers(self, driver, offers):
        if self.running:
            for offer in offers:
                driver.declineOffer(offer.id)
                return

        for offer, r in map(lambda x: self.convert_offer(x), offers):
            logging.info("offer: id={0} resources={1}".format(
                offer.id.value, r))

            missed_resources = \
                {k: v for k,v in self.resources.iteritems() if r.get(k, 0) < v}
            if len(missed_resources.items()) > 0:
                logging.info("unused_offer: {0}".format(missed_resources))
                driver.declineOffer(offer.id)
                continue

            if len(r.get("ports", [])) == 0:
                logging.info("no_ports: {0}".format(r))
                driver.declineOffer(offer.id)
                continue

            task = self.make_task(offer)
            logging.info("launch_task: hostname={0}".format(offer.hostname))
            driver.launchTasks(offer.id, [task])
            self.running = True

    def statusUpdate(self, driver, status):
        # if status.state == mesos_pb2.TASK_RUNNING:
        #     return

        print(status)

    def make_task(self, offer):
        docker = mesos_pb2.ContainerInfo.DockerInfo()
        docker.image = "thomasr/sleep"

        container = mesos_pb2.ContainerInfo(
            docker = docker,
            type = 1
        )

        task = mesos_pb2.TaskInfo(
            slave_id = offer.slave_id,
            container = container,
            command = mesos_pb2.CommandInfo(
                shell = False
            )
        )
        name = "{0}.server".format(self.name)
        task.task_id.value = name
        task.name = name

        for k, v in self.resources.items():
            r = task.resources.add()
            r.name = k
            r.type = mesos_pb2.Value.SCALAR
            r.scalar.value = v
            r.role = self.role

        return task


CURRENT = VPNScheduler()
