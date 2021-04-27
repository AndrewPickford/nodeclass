from py.test import raises

from reclass.interpolator import Interpolators
from reclass.node.klass import Klass
from reclass.settings import defaults, Settings
from reclass.value.exceptions import MergeOverImmutableError, MergeTypeError


interpolator_default = Interpolators.Full(defaults)

def cpar(parameters_dict):
    return Klass({'parameters': parameters_dict}, '')

def merge(base, merge, interpolator = interpolator_default):
    classes = [ cpar(base), cpar(merge) ]
    merged = interpolator.merge(classes)
    return merged.render_all()


def test_merge_scalars():
    result = merge(
        {'a': 1, 'b': 'b'},    # base dict
        {'c': 2, 'd': 'd'})    # dict to merge over base
    expected = {'a': 1, 'b': 'b', 'c': 2, 'd': 'd'}
    assert result == expected

def test_merge_scalars_overwrite():
    result = merge(
        {'a': 1, 'b': 2, 'c': 3},
        {'a': 4, 'b': 1})
    expected = {'a': 4, 'b': 1, 'c': 3}
    assert result == expected

def test_merge_lists():
    result = merge(
        {'a': [1, 2, 3]},
        {'a': [4, 5, 6]})
    expected = {'a': [1, 2, 3, 4, 5, 6]}
    assert result == expected

def test_merge_list_scalar():
    with raises(MergeTypeError):
        merge(
            {'a': [1, 2, 3]},
            {'a': 1})

def test_merge_scalar_list():
    with raises(MergeTypeError):
        merge(
            {'a': 1},
            {'a': [1, 2, 3]})

def test_merge_dicts_different_keys():
    result = merge(
        {'a': { 'one': 1, 'two': 2, 'three': 3 }},
        {'a': { 'four': 4, 'five': 5, 'six': 6 }} )
    expected = {'a': { 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6}}
    assert result == expected

def test_merge_dicts_common_keys():
    result = merge(
        {'a': { 'alpha': 1, 'beta': 2, 'gamma': 3 }},
        {'a': { 'alpha': 4, 'gamma': 5 }})
    expected = {'a': { 'alpha': 4, 'beta': 2, 'gamma': 5}}
    assert result == expected

def test_merge_dict_scalar():
    with raises(MergeTypeError):
        merge(
            {'a': { 'one': 1, 'two': 2, 'three': 3}},
            {'a': 1})

def test_merge_scalar_dict():
    with raises(MergeTypeError):
        merge(
            {'a': 1},
            {'a': { 'one': 1, 'two': 2, 'three': 3}})

def test_merge_dict_list():
    with raises(MergeTypeError):
        merge(
            {'a': { 'one': 1, 'two': 2, 'three': 3}},
            {'a': [1, 2, 3]})

def test_merge_list_dict():
    with raises(MergeTypeError):
        merge(
            {'a': [1, 2, 3]},
            {'a': { 'one': 1, 'two': 2, 'three': 3}})

def test_merge_allow_none_overwrite_false():
    interpolator = Interpolators.Full(Settings({'allow_none_overwrite': False}))
    with raises(MergeTypeError):
        merge(
            {'a': None},
            {'a': [1, 2, 3]},
            interpolator = interpolator)
    with raises(MergeTypeError):
        merge(
            {'a': None},
            {'a': { 'x': 'x', 'y': 'y'}},
            interpolator = interpolator)

def test_merge_allow_none_overwrite_true():
    interpolator = Interpolators.Full(Settings({'allow_none_overwrite': True}))
    result = merge(
        {'a': None, 'b': None, 'c': None},
        {'a': 'abc', 'b': [1, 2, 3], 'c': {'x': 'x', 'y': 'y'}},
        interpolator = interpolator)
    expected = {'a': 'abc', 'b': [1, 2, 3], 'c': {'x': 'x', 'y': 'y'}}
    assert result == expected

def test_merge_overwrite_prefix():
    result = merge(
        {'one': {'b': 'beta'}, 'two': ['delta']},
        {'~one': {'a': 'alpha'}, '~two': ['gamma']})
    expected = {'one': {'a': 'alpha'}, 'two': ['gamma']}
    assert result == expected

def test_merge_immutable_prefix():
    with raises(MergeOverImmutableError):
        merge(
            {'=one': 1},
            {'one': 2})
