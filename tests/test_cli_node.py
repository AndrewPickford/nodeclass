import os
import subprocess
import yaml
from contextlib import contextmanager
from .node_1 import node_1

SafeLoader = yaml.CSafeLoader if yaml.__with_libyaml__ else yaml.SafeLoader

directory = os.path.dirname(os.path.realpath(__file__))


@contextmanager
def set_working_directory(path):
    origin = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)

def test_cli_node():
    with set_working_directory(directory):
        cmd_path = os.path.abspath(os.path.join('..', 'nodeclass.py'))
        config_path = 'nodeclass-config-001.yml'
        process = subprocess.run([cmd_path, 'node', 'node_1', '--config-filename', 'nodeclass-config-001.yml'], capture_output=True)
    output = yaml.load(process.stdout, Loader=SafeLoader)
    assert(output == node_1)
