from py.test import raises

from reclass.controller import Controller
from reclass.interpolator.exceptions import InterpolationCircularReferenceError
from reclass.node.klass import Klass
from reclass.node.protoklass import ProtoKlass
from reclass.settings import defaults, Settings
from reclass.value.exceptions import MergeOverImmutableError, MergeTypeError


controller_default = Controller(defaults)

def kpar(parameters_dict, controller):
    proto = ProtoKlass(name='', class_dict={}, url ='')
    parameters = controller.value_factory.make_value_dictionary(parameters_dict, proto.url)
    exports = controller.value_factory.make_value_dictionary({}, proto.url)
    return Klass(proto, parameters, exports)

def resolve_parameters(*dicts, inventory = None, controller = controller_default):
    '''
    dicts: one or more dicts to merge and resolve
    inventory: inventory to use during the resolve step
    controller: master controller
    '''
    klasses = [ kpar(k, controller) for k in dicts ]
    inventory = None
    merged_parameters = controller.interpolator.merger.merge_parameters(klasses)
    resolved_parameters = controller.interpolator.parameters_resolver.resolve(environment = None, parameters = merged_parameters, inventory = inventory)
    return resolved_parameters.render_all()


def test_parameters_resolver_single():
    result = resolve_parameters({'a': '${b}', 'b': 42})
    expected = {'a': 42, 'b': 42}
    assert result == expected

def test_parameters_resolver_composite():
    result = resolve_parameters({'a': '${b}${c}', 'b': '4', 'c': '2'})
    expected = {'a': '42', 'b': '4', 'c': '2'}
    assert result == expected

def test_parameters_resolver_composite_to_str():
    result = resolve_parameters({'a': '${b}${c}', 'b': 4, 'c': 2})
    expected = {'a': '42', 'b': 4, 'c': 2}
    assert result == expected

def test_parameters_resolver_chained_ref():
    result = resolve_parameters({'a': '${b}', 'b': '${c}', 'c': 42})
    expected = {'a': 42, 'b': 42, 'c': 42}
    assert result == expected

def test_parameters_resolver_ref_list():
    result = resolve_parameters({'a': '${b}', 'b': [41, 42, 43]})
    expected = {'a': [41, 42, 43], 'b': [41, 42, 43]}
    assert result == expected

def test_parameters_resolver_circular_references():
    with raises(InterpolationCircularReferenceError) as exc_info:
        resolve_parameters({'a': '${b}', 'b': '${a}'})
    # interpolation can start with foo or bar
    assert (str(exc_info.value.path), str(exc_info.value.reference)) in \
           [('a', 'b'), ('b', 'a')]

def test_parameters_resolver_nested_references():
    result = resolve_parameters({'a': '${${c}}', 'b': 42, 'c': 'b'})
    expected = {'a': 42, 'b': 42, 'c': 'b'}
    assert result == expected

def test_parameters_resolver_nested_deep_references():
    result = resolve_parameters({'one': {'a': 1, 'b': '${one:${one:c}}', 'c': 'a'}})
    expected = {'one': {'a': 1, 'b': 1, 'c': 'a'}}
    assert result == expected

def test_parameters_resolver_no_stray_overwrites_during_interpolation():
    result = resolve_parameters(
        {'a' : 1, 'b': '${a}'},
        {'a' : 1, 'b': 2})
    expected = {'a' : 1, 'b': 2}
    assert result == expected

def test_parameters_resolver_referenced_dict_deep_overwrite():
    result = resolve_parameters(
        {'alpha': {'one': {'a': 1, 'b': 2}}},
        {'beta': '${alpha}'},
        {'alpha': {'one': {'c': 3, 'd': 4}}, 'beta': {'one': {'a': 99}}})
    expected = {'alpha': {'one': {'a':1, 'b': 2, 'c': 3, 'd':4}},
                'beta': {'one': {'a':99, 'b': 2, 'c': 3, 'd':4}}}
    assert result == expected

def test_parameters_resolver_complex_reference_overwriting():
    result = resolve_parameters(
        {'one': 'abc_123_${two}_${three}', 'two': 'XYZ', 'four': 4},
        {'one': 'QWERTY_${three}_${four}', 'three': '999'})
    expected = {'one': 'QWERTY_999_4', 'two': 'XYZ', 'three': '999', 'four': 4}
    assert result == expected

def test_parameters_resolver_nested_reference_with_overwriting():
    result = resolve_parameters(
        {'one': {'a': 1, 'b': 2, 'z': 'a'}, 'two': '${one:${one:z}}'},
        {'one': {'z': 'b'}})
    expected = {'one': {'a': 1, 'b':2, 'z': 'b'}, 'two': 2}
    assert result == expected

def test_parameters_resolver_referenced_lists():
    result = resolve_parameters(
        {'one': [1, 2, 3], 'two': [4, 5, 6], 'three': '${one}'},
        {'three': '${two}'})
    expected = {'one': [1, 2, 3], 'two': [4, 5, 6], 'three': [1, 2, 3, 4, 5, 6]}
    assert result == expected

def test_parameters_resolver_referenced_dicts():
    result = resolve_parameters(
        {'one': {'a': 1, 'b': 2}, 'two': {'c': 3, 'd': 4}, 'three': '${one}'},
        {'three': '${two}'})
    expected = {'one': {'a': 1, 'b': 2}, 'two': {'c': 3, 'd': 4},
                'three': {'a': 1, 'b': 2, 'c': 3, 'd': 4}}
    assert result == expected

def test_parameters_resolver_deep_refs_in_referenced_dicts():
    result = resolve_parameters(
        {'one': '${three:a}', 'two': {'a': 1, 'b': 2}, 'three': '${two}'})
    expected = {'one': 1, 'two': {'a': 1, 'b': 2}, 'three': {'a': 1, 'b': 2}}
    assert result == expected

def test_parameters_resolver_allow_none_overwrite_false():
    controller = Controller(Settings({'allow_none_overwrite': False}))
    with raises(MergeTypeError):
        resolve_parameters(
            {'a': None},
            {'a': [1, 2, 3]},
            controller = controller)
    with raises(MergeTypeError):
        resolve_parameters(
            {'a': None},
            {'a': { 'x': 'x', 'y': 'y'}},
            controller = controller)
    with raises(MergeTypeError):
        resolve_parameters(
            {'a': None},
            {'a': '${b}', 'b': [1, 2, 3]},
            controller = controller)
    with raises(MergeTypeError):
        resolve_parameters(
            {'a': None},
            {'a': '${b}', 'b': { 'x': 'x', 'y': 'y'}},
            controller = controller)

def test_parameters_resolver_allow_none_overwrite_true():
    controller = Controller(Settings({'allow_none_overwrite': True}))
    result = resolve_parameters(
        {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None},
        {'a': 'abc', 'b': [1, 2, 3], 'c': {'a': 'aaa', 'b': 'bbb'}, 'd': '${a}', 'e': '${b}', 'f': '${c}'},
        controller = controller)
    expected = {'a': 'abc', 'b': [1, 2, 3], 'c': {'a': 'aaa', 'b': 'bbb'}, 'd': 'abc', 'e': [1, 2, 3], 'f': {'a': 'aaa', 'b': 'bbb'}}
    assert result == expected

def test_parameters_resolver_overwrite_prefix():
    result = resolve_parameters(
        {'a': '${b}', 'b': {'x': 'x', 'y': 'y'}, 'c': '${d}', 'd': [1, 2, 3]},
        {'~a': {'z': 'z'}, '~c': [4, 5, 6]})
    expected = {'a': {'z': 'z'}, 'b': {'x': 'x', 'y': 'y'}, 'c': [4, 5, 6], 'd': [1, 2, 3]}
    assert result == expected

def test_parameters_resolver_immutable_prefix():
    with raises(MergeOverImmutableError):
        resolve_parameters(
            {'=a': '${b}', 'b': {'x': 'x', 'y': 'y'}},
            {'a': {'z': 'z'}})
    with raises(MergeOverImmutableError):
        resolve_parameters(
            {'=c': '${d}', 'd': [1, 2, 3]},
            {'c': [4, 5, 6]})

def test_parameters_resolver_escaping():
    result = resolve_parameters({'a': '\${b}', 'b': 'bb'})
    expected = {'a': '${b}', 'b': 'bb'}
    assert result == expected
