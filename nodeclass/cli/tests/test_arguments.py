import pytest
from nodeclass.cli.config import process_args
from nodeclass.cli.parser import make_parser
from nodeclass.cli.exceptions import BadArguments

def test_arguments_simple_uri():
    parser = make_parser()
    args = parser.parse_args(['node', 'test', '--uri', 'yaml_fs:/test'])
    settings, uri = process_args(args)
    assert(uri == 'yaml_fs:/test')

def test_arguments_split_uri():
    parser = make_parser()
    args = parser.parse_args(['node', 'test', '--uri-classes', 'yaml_fs:/test/classes', '--uri-nodes', 'yaml_fs:/test/nodes'])
    settings, uri = process_args(args)
    assert(uri == {'classes': 'yaml_fs:/test/classes', 'nodes': 'yaml_fs:/test/nodes'})

def test_arguments_invalid_uri():
    parser = make_parser()
    with pytest.raises(BadArguments):
        args = parser.parse_args(['node', 'test', '--uri', 'yaml_fs:/test', '--uri-classes', 'yaml_fs:/test/classes'])
        settings, uri = process_args(args)
    with pytest.raises(BadArguments):
        args = parser.parse_args(['node', 'test', '--uri', 'yaml_fs:/test', '--uri-nodes', 'yaml_fs:/test/nodes'])
        settings, uri = process_args(args)
    with pytest.raises(BadArguments):
        args = parser.parse_args(['node', 'test', '--uri-classes', 'yaml_fs:/test/classes'])
        settings, uri = process_args(args)
    with pytest.raises(BadArguments):
        args = parser.parse_args(['node', 'test', '--uri-nodes', 'yaml_fs:/test/nodes'])
        settings, uri = process_args(args)
