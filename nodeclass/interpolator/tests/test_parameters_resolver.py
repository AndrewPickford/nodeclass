import copy
import pytest
from nodeclass.context import nodeclass_context
from nodeclass.interpolator.exceptions import CircularReference, NoSuchReference
from nodeclass.interpolator.parameters_resolver import ParametersResolver
from nodeclass.node.klass import Klass
from nodeclass.settings import Settings
from nodeclass.utils.path import Path
from nodeclass.value.exceptions import MergeOverImmutable, MergeIncompatibleTypes
from nodeclass.value.hierarchy import Hierarchy

parameters_resolver = ParametersResolver()
settings = Settings()

def kpar(parameters, index):
    class_dict = { 'exports': {}, 'parameters': parameters }
    return Klass.from_class_dict(name='', class_dict=class_dict, url='test_url_{0}'.format(index))

def resolve_parameters(*dicts, inventory = None):
    '''
    dicts: one or more dicts to merge and resolve
    inventory: inventory to use during the resolve step
    '''
    klasses = [ kpar(k, i) for i, k in enumerate(dicts) ]
    inventory = None
    merged_parameters = Hierarchy.merge_multiple([ klass.parameters for klass in klasses ], 'parameters')
    resolved_parameters = parameters_resolver.resolve(environment = None, parameters = merged_parameters, inventory = inventory)
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
    with pytest.raises(CircularReference) as info:
        resolve_parameters({'a': '${b}', 'b': '${a}'})
    assert info.value.url == 'test_url_0'
    assert info.value.hierarchy_type == 'parameters'
    # interpolation can start with parameter a or b
    assert (info.value.path == Path.fromstring('a') and info.value.reference == Path.fromstring('b')) or \
           (info.value.path == Path.fromstring('b') and info.value.reference == Path.fromstring('a'))

def test_parameters_resolver_missing_reference():
    with pytest.raises(NoSuchReference) as info:
        resolve_parameters({'a': '${b}'})
    assert info.value.url == 'test_url_0'
    assert info.value.hierarchy_type == 'parameters'
    assert info.value.path == Path.fromstring('a')
    assert info.value.reference == Path.fromstring('b')

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
    with nodeclass_context(Settings({'allow_none_overwrite': False})):
        with pytest.raises(MergeIncompatibleTypes):
            resolve_parameters(
                {'a': None},
                {'a': [1, 2, 3]})
        with pytest.raises(MergeIncompatibleTypes):
            resolve_parameters(
                {'a': None},
                {'a': { 'x': 'x', 'y': 'y'}})
        with pytest.raises(MergeIncompatibleTypes):
            resolve_parameters(
                {'a': None},
                {'a': '${b}', 'b': [1, 2, 3]})
        with pytest.raises(MergeIncompatibleTypes):
            resolve_parameters(
                {'a': None},
                {'a': '${b}', 'b': { 'x': 'x', 'y': 'y'}})

def test_parameters_resolver_allow_none_overwrite_true():
    with nodeclass_context(Settings({'allow_none_overwrite': True})):
        result = resolve_parameters(
            {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None},
            {'a': 'abc', 'b': [1, 2, 3], 'c': {'a': 'aaa', 'b': 'bbb'}, 'd': '${a}', 'e': '${b}', 'f': '${c}'})
        expected = {'a': 'abc', 'b': [1, 2, 3], 'c': {'a': 'aaa', 'b': 'bbb'}, 'd': 'abc', 'e': [1, 2, 3], 'f': {'a': 'aaa', 'b': 'bbb'}}
        assert result == expected

def test_parameters_resolver_overwrite_prefix():
    result = resolve_parameters(
        {'a': '${b}', 'b': {'x': 'x', 'y': 'y'}, 'c': '${d}', 'd': [1, 2, 3]},
        {'~a': {'z': 'z'}, '~c': [4, 5, 6]})
    expected = {'a': {'z': 'z'}, 'b': {'x': 'x', 'y': 'y'}, 'c': [4, 5, 6], 'd': [1, 2, 3]}
    assert result == expected

def test_parameters_resolver_immutable_prefix():
    with pytest.raises(MergeOverImmutable):
        resolve_parameters(
            {'=a': '${b}', 'b': {'x': 'x', 'y': 'y'}},
            {'a': {'z': 'z'}})
    with pytest.raises(MergeOverImmutable):
        resolve_parameters(
            {'=c': '${d}', 'd': [1, 2, 3]},
            {'c': [4, 5, 6]})

def test_parameters_resolver_escaping():
    result = resolve_parameters({
        'a': settings.escape_character + '${b}',
        'b': 'unused'})
    expected = {'a': '${b}', 'b': 'unused'}
    assert result == expected

def test_parameters_resolver_double_escaping():
    result = resolve_parameters({
        'a': settings.escape_character + settings.escape_character + '${b}',
        'b': 'bb'})
    expected = {
        'a': settings.escape_character + 'bb',
        'b': 'bb'}
    assert result == expected

def test_parameters_resolver_ignore_escaping():
    ''' In all following cases, escaping should not happen and the escape character
        needs to be printed as-is, to ensure backwards compatibility to older nodeclass
        versions
    '''
    expected = {
        # Escape character followed by unescapable character
        'a': '1' + settings.escape_character + '1',
        # Escape character followed by escape character
        'b': '2' + settings.escape_character + settings.escape_character,
        # Escape character followed by interpolation end sentinel
        'c': '3' + settings.escape_character + '}',
        # Escape character at the end of the string
        'd': '4' + settings.escape_character }
    result = resolve_parameters(copy.copy(expected))
    assert result == expected

def test_parameters_resolver_escape_end_reference_sentinel_in_reference():
    result = resolve_parameters({
        'one}': 1,
        'two': '${one' + settings.escape_character + '}}' })
    expected = { 'one}': 1, 'two': 1 }
    assert result == expected

def test_parameters_resolver_double_escape_in_reference():
    result = resolve_parameters({
        'one' + settings.escape_character: 1,
        'two': '${one' + settings.escape_character + settings.escape_character + '}' })
    expected = { 'one' + settings.escape_character: 1, 'two': 1 }
    assert result == expected
