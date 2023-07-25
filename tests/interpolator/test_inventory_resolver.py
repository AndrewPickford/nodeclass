import pytest
from typing import NamedTuple
from nodeclass.interpolator.exceptions import InventoryQueryError
from nodeclass.interpolator.inventory_resolver import InventoryResolver
from nodeclass.interpolator.parameters_resolver import ParametersResolver
from nodeclass.invquery.parser import parse as parse_query
from nodeclass.value.hierarchy import Hierarchy

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Dict, List, Set

parameters_resolver = ParametersResolver()
inventory_resolver = InventoryResolver(parameters_resolver)

class InvResTestData(NamedTuple):
    exports: 'Dict'
    parameters: 'Dict'
    queries: 'List'
    name: 'str'
    expected_rendered: 'Dict'
    expected_failed: 'Set'
    expected_exception: 'bool'

def resolve_inventory(exports, parameters, queries, name):
    exports_hierarchy = Hierarchy.from_dict(exports, name, 'exports')
    parameters_hierarchy = Hierarchy.from_dict(parameters, name, 'parameters')
    queries_set = { parse_query(q) for q in queries }
    return inventory_resolver.resolve(exports_hierarchy, parameters_hierarchy, queries_set, name)

def render_paths(resolved, paths):
    pruned = resolved.extract(paths)
    return pruned.render_all()


inventory_resolver_test_data = [
    InvResTestData(
        # single value query
        exports = { 'a': '${a}' },
        parameters= { 'a': 1 },
        queries = [ 'exports:a' ],
        name = 'node1',
        expected_rendered = { 'a': 1 },
        expected_failed = set(),
        expected_exception = False
    ),
    InvResTestData(
        # single value if query
        exports = { 'a': '${a}', 'b': '${b}' },
        parameters = { 'a': 1, 'b': '${c}', 'c': 2 },
        queries = [ 'exports:a if exports:b == 1' ],
        name = 'node1',
        expected_rendered = { 'a': 1, 'b': 2 },
        expected_failed = set(),
        expected_exception = False
    ),
    InvResTestData(
        # single if query
        exports = { 'a': '${a}' },
        parameters = { 'a': '${b}', 'b': 2 },
        queries = [ 'if exports:a == 1' ],
        name = 'node1',
        expected_rendered = { 'a': 2 },
        expected_failed = set(),
        expected_exception = False
    ),
    InvResTestData(
        # single value query, bad reference
        exports = { 'a': '${b}' },
        parameters= { 'a': 1 },
        queries = [ 'exports:a' ],
        name = 'node1',
        expected_rendered = {},
        expected_failed = set(),
        expected_exception = True
    ),
    InvResTestData(
        # single value query, bad reference, ignore errors
        exports = { 'a': '${b}' },
        parameters= { 'a': 1 },
        queries = [ '+IgnoreErrors exports:a' ],
        name = 'node1',
        expected_rendered = {},
        expected_failed = { '+IgnoreErrors exports:a' },
        expected_exception = False
    ),
    InvResTestData(
        # single value, if and value if queries, all bad references, all ignore errors
        exports = { 'a': '${a}', 'b': '${b}', 'c': '${c}', 'd': '${d}' },
        parameters= {},
        queries = [ '+IgnoreErrors exports:a', '+IgnoreErrors exports:b if exports:c == 1', '+IgnoreErrors if exports:d == 1' ],
        name = 'node1',
        expected_rendered = {},
        expected_failed = { '+IgnoreErrors exports:a', '+IgnoreErrors exports:b if exports:c == 1', '+IgnoreErrors if exports:d == 1' },
        expected_exception = False
    ),
    InvResTestData(
        # if value query with bad reference, if value querys without corresponding exports
        exports = { 'a': '${a}', 'b': 1 },
        parameters= {},
        queries = [ '+IgnoreErrors exports:a if exports:b == 1', '+IgnoreErrors exports:c if exports:d == 1', '+IgnoreErrors exports:d if exports:c == 1'  ],
        name = 'node1',
        expected_rendered = { 'b': 1 },
        expected_failed = { '+IgnoreErrors exports:a if exports:b == 1' },
        expected_exception = False
    ),
    InvResTestData(
        # good if query, good value query, bad if value query with a bad reference
        exports = { 'a': '${a}', 'b': 2, 'c': '${c}' },
        parameters= { 'a': 1 },
        queries = [ 'if exports:a == 1', 'exports:b', '+IgnoreErrors exports:a if exports:c == 1' ],
        name = 'node1',
        expected_rendered = { 'a': 1, 'b': 2 },
        expected_failed = { '+IgnoreErrors exports:a if exports:c == 1' },
        expected_exception = False
    ),
    InvResTestData(
        # two bad value queries, one with IgnoreErrors
        exports = { 'a': '${a}' },
        parameters= {},
        queries = [ '+IgnoreErrors exports:a', 'exports:a' ],
        name = 'node1',
        expected_rendered = {},
        expected_failed = set(),
        expected_exception = True
    ),
]


@pytest.mark.parametrize('exports, parameters, queries, name, expected_rendered, expected_failed, expected_exception', inventory_resolver_test_data)
def test_inventory_resolver_test_data(exports, parameters, queries, name, expected_rendered, expected_failed, expected_exception):
    try:
        resolved, failed = resolve_inventory(exports, parameters, queries, name)
    except InventoryQueryError:
        if expected_exception:
            return
        else:
            raise
    paths = resolved.resolved_paths()
    rendered = render_paths(resolved, paths)
    failed = { str(q) for q in failed }
    assert failed == expected_failed
    assert rendered == expected_rendered
