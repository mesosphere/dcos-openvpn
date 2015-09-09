from __future__ import print_function
import json
import os
import os.path
import subprocess

import pkg_resources
from dcos_spark import constants

def partition(args, pred):
    ain = []
    aout = []
    for x in args:
        if pred(x):
            ain.append(x)
        else:
            aout.append(x)
    return (ain, aout)

def show_help():
    submit_file = pkg_resources.resource_filename(
        'dcos_spark',
        'data/' + constants.spark_version + '/bin/spark-submit')

    command = [submit_file, "--help"]

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    stdout, stderr = process.communicate()

    for line in stderr.split("\n"):
        if line.startswith("Usage:"):
            continue
        print(line)

    return 0


def submit_job(master, args):
    (props, args) = partition(args.split(" "), lambda a: a.startswith("-D"))
    props = props + ["-Dspark.mesos.executor.docker.image=" + constants.spark_mesos_image]
    response = run(master, args, props)
    if response[0] is not None:
        print("Run job succeeded. Submission id: " +
              response[0]['submissionId'])
    return response[1]


def job_status(master, submissionId):
    response = run(master, ["--status", submissionId])
    if response[0] is not None:
        print("Submission ID: " + response[0]['submissionId'])
        print("Driver state: " + response[0]['driverState'])
        if 'message' in response[0]:
            print("Last status: " + response[0]['message'])
    return response[1]


def kill_job(master, submissionId):
    response = run(master, ["--kill", submissionId])
    if response[0] is not None:
        if bool(response[0]['success']):
            success = "succeeded."
        else:
            success = "failed."
        print("Kill job " + success)
        print("Message: " + response[0]['message'])
    return response[1]


def which(program):
    """Returns the path to the named executable program.

    :param program: The program to locate:
    :type program: str
    :rtype: str
    """

    def is_exe(file_path):
        return os.path.isfile(file_path) and os.access(file_path, os.X_OK)

    file_path, filename = os.path.split(program)
    if file_path:
        if is_exe(program):
            return program
    elif constants.PATH_ENV in os.environ:
        for path in os.environ[constants.PATH_ENV].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def check_java():
    # Check if JAVA is in the PATH
    if which('java') is not None:
        return True

    # Check if JAVA_HOME is set and find java
    java_home = os.environ.get('JAVA_HOME')
    if java_home is not None and os.path.isfile(java_home + "/bin/java"):
        return True

    return False


def run(master, args, props = []):
    """
    This method runs spark_submit with the passed in parameters.
    ie: ./bin/spark-submit --deploy-mode cluster --class
    org.apache.spark.examples.SparkPi --master mesos://10.127.131.174:8077
    --executor-memory 1G --total-executor-cores 100 --driver-memory 1G
    http://10.127.131.174:8000/spark-examples_2.10-1.3.0-SNAPSHOT.jar 30
    """
    if not check_java():
        print("DCOS Spark requires Java to be installed. Please install JRE.")
        return (None, 1)

    submit_file = pkg_resources.resource_filename(
        'dcos_spark',
        'data/' + constants.spark_version + '/bin/spark-submit')

    command = [submit_file, "--deploy-mode", "cluster", "--master",
               "mesos://" + master] + args

    process = subprocess.Popen(
        command,
        env = dict(os.environ, **{"SPARK_JAVA_OPTS": ' '.join(props)}),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    stdout, stderr = process.communicate()

    if process.returncode != 0:
        print("Spark submit failed:")
        print(stderr)
        return (None, process.returncode)
    else:
        err = stderr.decode("utf-8")
        response = json.loads(err[err.index('{'):err.index('}') + 1])
        return (response, process.returncode)
