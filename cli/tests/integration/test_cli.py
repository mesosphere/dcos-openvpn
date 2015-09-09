from common import exec_command


def test_help():
    returncode, stdout, stderr = exec_command(
        ['dcos-spark', 'spark', '--help'])

    assert returncode == 0
    assert stderr == b''
