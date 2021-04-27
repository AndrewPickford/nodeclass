from py.test import raises

from reclass.interpolator import Interpolators
from reclass.interpolator.exceptions import InterpolationCircularReferenceError
from reclass.node.klass import Klass
from reclass.settings import defaults, Settings
from reclass.value.exceptions import MergeOverImmutableError, MergeTypeError


interpolator_default = Interpolators.Full(defaults)

def cpar(parameters_dict):
    return Klass({'parameters': parameters_dict}, '')

def interpolate(*dicts, interpolator = interpolator_default):
    '''
    dicts: one or more dicts to merge and interpolate
    interpolator: the interpolator to use or None to use a default
    '''
    classes = [ cpar(c) for c in dicts ]
    return interpolator.interpolate(classes, {})


def test_interpolate_single():
    result = interpolate({'a': '${b}', 'b': 42})
    expected = {'a': 42, 'b': 42}
    assert result == expected

def test_interpolate_composite():
    result = interpolate({'a': '${b}${c}', 'b': '4', 'c': '2'})
    expected = {'a': '42', 'b': '4', 'c': '2'}
    assert result == expected

def test_interpolate_composite_to_str():
    result = interpolate({'a': '${b}${c}', 'b': 4, 'c': 2})
    expected = {'a': '42', 'b': 4, 'c': 2}
    assert result == expected

def test_interpolate_chained_ref():
    result = interpolate({'a': '${b}', 'b': '${c}', 'c': 42})
    expected = {'a': 42, 'b': 42, 'c': 42}
    assert result == expected

def test_interpolate_ref_list():
    result = interpolate({'a': '${b}', 'b': [41, 42, 43]})
    expected = {'a': [41, 42, 43], 'b': [41, 42, 43]}
    assert result == expected

def test_interpolate_circular_references():
    with raises(InterpolationCircularReferenceError) as exc_info:
        interpolate({'a': '${b}', 'b': '${a}'})
    # interpolation can start with foo or bar
    assert (str(exc_info.value.path), str(exc_info.value.reference)) in \
           [('a', 'b'), ('b', 'a')]

def test_interpolate_nested_references():
    result = interpolate({'a': '${${c}}', 'b': 42, 'c': 'b'})
    expected = {'a': 42, 'b': 42, 'c': 'b'}
    assert result == expected

def test_interpolate_nested_deep_references():
    result = interpolate({'one': {'a': 1, 'b': '${one:${one:c}}', 'c': 'a'}})
    expected = {'one': {'a': 1, 'b': 1, 'c': 'a'}}
    assert result == expected

def test_interpolate_no_stray_overwrites_during_interpolation():
    result = interpolate(
        {'a' : 1, 'b': '${a}'},
        {'a' : 1, 'b': 2})
    expected = {'a' : 1, 'b': 2}
    assert result == expected

def test_interpolate_referenced_dict_deep_overwrite():
    result = interpolate(
        {'alpha': {'one': {'a': 1, 'b': 2}}},
        {'beta': '${alpha}'},
        {'alpha': {'one': {'c': 3, 'd': 4}}, 'beta': {'one': {'a': 99}}})
    expected = {'alpha': {'one': {'a':1, 'b': 2, 'c': 3, 'd':4}},
                'beta': {'one': {'a':99, 'b': 2, 'c': 3, 'd':4}}}
    assert result == expected

def test_interpolate_complex_reference_overwriting():
    result = interpolate(
        {'one': 'abc_123_${two}_${three}', 'two': 'XYZ', 'four': 4},
        {'one': 'QWERTY_${three}_${four}', 'three': '999'})
    expected = {'one': 'QWERTY_999_4', 'two': 'XYZ', 'three': '999', 'four': 4}
    assert result == expected

def test_interpolate_nested_reference_with_overwriting():
    result = interpolate(
        {'one': {'a': 1, 'b': 2, 'z': 'a'}, 'two': '${one:${one:z}}'},
        {'one': {'z': 'b'}})
    expected = {'one': {'a': 1, 'b':2, 'z': 'b'}, 'two': 2}
    assert result == expected

def test_interpolate_referenced_lists():
    result = interpolate(
        {'one': [1, 2, 3], 'two': [4, 5, 6], 'three': '${one}'},
        {'three': '${two}'})
    expected = {'one': [1, 2, 3], 'two': [4, 5, 6], 'three': [1, 2, 3, 4, 5, 6]}
    assert result == expected

def test_interpolate_referenced_dicts():
    result = interpolate(
        {'one': {'a': 1, 'b': 2}, 'two': {'c': 3, 'd': 4}, 'three': '${one}'},
        {'three': '${two}'})
    expected = {'one': {'a': 1, 'b': 2}, 'two': {'c': 3, 'd': 4},
                'three': {'a': 1, 'b': 2, 'c': 3, 'd': 4}}
    assert result == expected

def test_interpolate_deep_refs_in_referenced_dicts():
    result = interpolate(
        {'one': '${three:a}', 'two': {'a': 1, 'b': 2}, 'three': '${two}'})
    expected = {'one': 1, 'two': {'a': 1, 'b': 2}, 'three': {'a': 1, 'b': 2}}
    assert result == expected

def test_interpolate_allow_none_overwrite_false():
    interpolator = Interpolators.Full(Settings({'allow_none_overwrite': False}))
    with raises(MergeTypeError):
        interpolate(
            {'a': None},
            {'a': [1, 2, 3]},
            interpolator = interpolator)
    with raises(MergeTypeError):
        interpolate(
            {'a': None},
            {'a': { 'x': 'x', 'y': 'y'}},
            interpolator = interpolator)
    with raises(MergeTypeError):
        interpolate(
            {'a': None},
            {'a': '${b}', 'b': [1, 2, 3]},
            interpolator = interpolator)
    with raises(MergeTypeError):
        interpolate(
            {'a': None},
            {'a': '${b}', 'b': { 'x': 'x', 'y': 'y'}},
            interpolator = interpolator)

def test_interpolate_allow_none_overwrite_true():
    interpolator = Interpolators.Full(Settings({'allow_none_overwrite': True}))
    result = interpolate(
        {'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None},
        {'a': 'abc', 'b': [1, 2, 3], 'c': {'a': 'aaa', 'b': 'bbb'}, 'd': '${a}', 'e': '${b}', 'f': '${c}'},
        interpolator = interpolator)
    expected = {'a': 'abc', 'b': [1, 2, 3], 'c': {'a': 'aaa', 'b': 'bbb'}, 'd': 'abc', 'e': [1, 2, 3], 'f': {'a': 'aaa', 'b': 'bbb'}}
    assert result == expected

def test_interpolate_overwrite_prefix():
    result = interpolate(
        {'a': '${b}', 'b': {'x': 'x', 'y': 'y'}, 'c': '${d}', 'd': [1, 2, 3]},
        {'~a': {'z': 'z'}, '~c': [4, 5, 6]})
    expected = {'a': {'z': 'z'}, 'b': {'x': 'x', 'y': 'y'}, 'c': [4, 5, 6], 'd': [1, 2, 3]}
    assert result == expected

def test_interpolate_immutable_prefix():
    with raises(MergeOverImmutableError):
        interpolate(
            {'=a': '${b}', 'b': {'x': 'x', 'y': 'y'}},
            {'a': {'z': 'z'}})
    with raises(MergeOverImmutableError):
        interpolate(
            {'=c': '${d}', 'd': [1, 2, 3]},
            {'c': [4, 5, 6]})

def test_interpolate_escaping():
    result = interpolate({'a': '\${b}', 'b': 'bb'})
    expected = {'a': '${b}', 'b': 'bb'}
    assert result == expected
