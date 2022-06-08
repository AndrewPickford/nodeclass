import pytest
from reclass.cli.arguments import make_argparser, process_args
from reclass.cli.exceptions import BadArguments

def test_arguments_simple_uri():
    parser = make_argparser()
    args = parser.parse_args(['--nodeinfo', 'test', '--uri', 'yaml_fs:/test'])
    settings, uri = process_args(args)
    assert(uri == 'yaml_fs:/test')

def test_arguments_split_uri():
    parser = make_argparser()
    args = parser.parse_args(['--nodeinfo', 'test', '--uri-classes', 'yaml_fs:/test/classes', '--uri-nodes', 'yaml_fs:/test/nodes'])
    settings, uri = process_args(args)
    assert(uri == {'classes': 'yaml_fs:/test/classes', 'nodes': 'yaml_fs:/test/nodes'})

def test_arguments_invalid_uri():
    parser = make_argparser()
    with pytest.raises(BadArguments):
        args = parser.parse_args(['--nodeinfo', 'test', '--uri', 'yaml_fs:/test', '--uri-classes', 'yaml_fs:/test/classes'])
        settings, uri = process_args(args)
    with pytest.raises(BadArguments):
        args = parser.parse_args(['--nodeinfo', 'test', '--uri', 'yaml_fs:/test', '--uri-nodes', 'yaml_fs:/test/nodes'])
        settings, uri = process_args(args)
    with pytest.raises(BadArguments):
        args = parser.parse_args(['--nodeinfo', 'test', '--uri-classes', 'yaml_fs:/test/classes'])
        settings, uri = process_args(args)
    with pytest.raises(BadArguments):
        args = parser.parse_args(['--nodeinfo', 'test', '--uri-nodes', 'yaml_fs:/test/nodes'])
        settings, uri = process_args(args)
