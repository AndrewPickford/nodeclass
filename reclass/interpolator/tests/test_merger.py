import pytest
from reclass.context import reclass_context
from reclass.interpolator.merger import Merger
from reclass.node.klass import Klass
from reclass.node.protoklass import ProtoKlass
from reclass.settings import Settings
from reclass.value.exceptions import MergeOverImmutableError, MergeTypeError
from reclass.value.make import make_value_dictionary

reclass_context(Settings())
merger = Merger()

def kpar(parameters_dict):
    proto = ProtoKlass(name='', class_dict={}, url ='')
    parameters = make_value_dictionary(parameters_dict, proto.url)
    exports = make_value_dictionary({}, proto.url)
    return Klass(proto, parameters, exports)

def kexp(exports_dict):
    proto = ProtoKlass(name='', class_dict={}, url ='')
    parameters = make_value_dictionary({}, proto.url)
    exports = make_value_dictionary(exports_dict, proto.url)
    return Klass(proto, parameters, exports)

def merge_parameters(base, merge):
    klasses = [ kpar(base), kpar(merge) ]
    merged = merger.merge_parameters(klasses)
    return merged

def merge_exports(base, merge):
    klasses = [ kexp(base), kexp(merge) ]
    merged = merger.merge_exports(klasses)
    return merged

merge_test_types = (merge_parameters, merge_exports)


@pytest.mark.parametrize('merge_func', merge_test_types)
def test_merge_scalars(merge_func):
    result = merge_func(
        {'a': 1, 'b': 'b'},    # base dict
        {'c': 2, 'd': 'd'})    # dict to merge over base
    expected = {'a': 1, 'b': 'b', 'c': 2, 'd': 'd'}
    result = result.render_all()
    assert result == expected

@pytest.mark.parametrize('merge_func', merge_test_types)
def test_merge_scalars_overwrite(merge_func):
    result = merge_func(
        {'a': 1, 'b': 2, 'c': 3},
        {'a': 4, 'b': 1})
    expected = {'a': 4, 'b': 1, 'c': 3}
    result = result.render_all()
    assert result == expected

@pytest.mark.parametrize('merge_func', merge_test_types)
def test_merge_lists(merge_func):
    result = merge_func(
        {'a': [1, 2, 3]},
        {'a': [4, 5, 6]})
    expected = {'a': [1, 2, 3, 4, 5, 6]}
    result = result.render_all()
    assert result == expected

@pytest.mark.parametrize('merge_func', merge_test_types)
def test_merge_list_scalar(merge_func):
    with pytest.raises(MergeTypeError):
        merge_func(
            {'a': [1, 2, 3]},
            {'a': 1})

@pytest.mark.parametrize('merge_func', merge_test_types)
def test_merge_scalar_list(merge_func):
    with pytest.raises(MergeTypeError):
        merge_func(
            {'a': 1},
            {'a': [1, 2, 3]})

@pytest.mark.parametrize('merge_func', merge_test_types)
def test_merge_dicts_different_keys(merge_func):
    result = merge_func(
        {'a': { 'one': 1, 'two': 2, 'three': 3 }},
        {'a': { 'four': 4, 'five': 5, 'six': 6 }} )
    expected = {'a': { 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6}}
    result = result.render_all()
    assert result == expected

@pytest.mark.parametrize('merge_func', merge_test_types)
def test_merge_dicts_common_keys(merge_func):
    result = merge_func(
        {'a': { 'alpha': 1, 'beta': 2, 'gamma': 3 }},
        {'a': { 'alpha': 4, 'gamma': 5 }})
    expected = {'a': { 'alpha': 4, 'beta': 2, 'gamma': 5}}
    result = result.render_all()
    assert result == expected

@pytest.mark.parametrize('merge_func', merge_test_types)
def test_merge_dict_scalar(merge_func):
    with pytest.raises(MergeTypeError):
        merge_func(
            {'a': { 'one': 1, 'two': 2, 'three': 3}},
            {'a': 1})

@pytest.mark.parametrize('merge_func', merge_test_types)
def test_merge_scalar_dict(merge_func):
    with pytest.raises(MergeTypeError):
        merge_func(
            {'a': 1},
            {'a': { 'one': 1, 'two': 2, 'three': 3}})

@pytest.mark.parametrize('merge_func', merge_test_types)
def test_merge_dict_list(merge_func):
    with pytest.raises(MergeTypeError):
        merge_func(
            {'a': { 'one': 1, 'two': 2, 'three': 3}},
            {'a': [1, 2, 3]})

@pytest.mark.parametrize('merge_func', merge_test_types)
def test_merge_list_dict(merge_func):
    with pytest.raises(MergeTypeError):
        merge_func(
            {'a': [1, 2, 3]},
            {'a': { 'one': 1, 'two': 2, 'three': 3}})

@pytest.mark.parametrize('merge_func', merge_test_types)
def test_merge_allow_none_overwrite_false(merge_func):
    with reclass_context(Settings({'allow_none_overwrite': False})):
        with pytest.raises(MergeTypeError):
            merge_func(
                {'a': None},
                {'a': [1, 2, 3]})
        with pytest.raises(MergeTypeError):
            merge_func(
                {'a': None},
                {'a': { 'x': 'x', 'y': 'y'}})

@pytest.mark.parametrize('merge_func', merge_test_types)
def test_merge_allow_none_overwrite_true(merge_func):
    with reclass_context(Settings({'allow_none_overwrite': True})):
        result = merge_func(
            {'a': None, 'b': None, 'c': None},
            {'a': 'abc', 'b': [1, 2, 3], 'c': {'x': 'x', 'y': 'y'}})
        expected = {'a': 'abc', 'b': [1, 2, 3], 'c': {'x': 'x', 'y': 'y'}}
        result = result.render_all()
        assert result == expected

@pytest.mark.parametrize('merge_func', merge_test_types)
def test_merge_overwrite_prefix(merge_func):
    result = merge_func(
        {'one': {'b': 'beta'}, 'two': ['delta']},
        {'~one': {'a': 'alpha'}, '~two': ['gamma']})
    expected = {'one': {'a': 'alpha'}, 'two': ['gamma']}
    result = result.render_all()
    assert result == expected

@pytest.mark.parametrize('merge_func', merge_test_types)
def test_merge_immutable_prefix(merge_func):
    with pytest.raises(MergeOverImmutableError):
        merge_func(
            {'=one': 1},
            {'one': 2})
