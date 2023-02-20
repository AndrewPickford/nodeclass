import copy
import pytest
from nodeclass.context import nodeclass_context
from nodeclass.settings import Settings
from nodeclass.utils.path import Path
from nodeclass.value.exceptions import FrozenHierarchy, MergeOverImmutable, MergeIncompatibleTypes
from nodeclass.value.hierarchy import Hierarchy

nodeclass_context(Settings())

def merge_dicts(*dicts):
    top_dicts = [ Hierarchy.from_dict(d, '', '') for d in dicts ]
    merged = copy.copy(top_dicts[0])
    for d in top_dicts[1:]:
        merged.merge(d)
    return merged

def merge_top_dicts(*top_dicts):
    merged = copy.copy(top_dicts[0])
    for d in top_dicts[1:]:
        merged.merge(d)
    return merged

def test_merge_scalars():
    result = merge_dicts(
        {'a': 1, 'b': 'b'},
        {'c': 2, 'd': 'd'})
    expected = {'a': 1, 'b': 'b', 'c': 2, 'd': 'd'}
    result = result.render_all()
    assert result == expected

def test_merge_scalars_overwrite():
    result = merge_dicts(
        {'a': 1, 'b': 2, 'c': 3},
        {'a': 4, 'b': 1})
    expected = {'a': 4, 'b': 1, 'c': 3}
    result = result.render_all()
    assert result == expected

def test_merge_lists():
    result = merge_dicts(
        {'a': [1, 2, 3]},
        {'a': [4, 5, 6]})
    expected = {'a': [1, 2, 3, 4, 5, 6]}
    result = result.render_all()
    assert result == expected

def test_merge_list_scalar():
    with pytest.raises(MergeIncompatibleTypes):
        merge_dicts(
            {'a': [1, 2, 3]},
            {'a': 1})

def test_merge_scalar_list():
    with pytest.raises(MergeIncompatibleTypes):
        merge_dicts(
            {'a': 1},
            {'a': [1, 2, 3]})

def test_merge_dicts_different_keys():
    result = merge_dicts(
        {'a': { 'one': 1, 'two': 2, 'three': 3 }},
        {'a': { 'four': 4, 'five': 5, 'six': 6 }} )
    expected = {'a': { 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6}}
    result = result.render_all()
    assert result == expected

def test_merge_dicts_common_keys():
    result = merge_dicts(
        {'a': { 'alpha': 1, 'beta': 2, 'gamma': 3 }},
        {'a': { 'alpha': 4, 'gamma': 5 }})
    expected = {'a': { 'alpha': 4, 'beta': 2, 'gamma': 5}}
    result = result.render_all()
    assert result == expected

def test_merge_dict_scalar():
    with pytest.raises(MergeIncompatibleTypes):
        merge_dicts(
            {'a': { 'one': 1, 'two': 2, 'three': 3}},
            {'a': 1})

def test_merge_scalar_dict():
    with pytest.raises(MergeIncompatibleTypes):
        merge_dicts(
            {'a': 1},
            {'a': { 'one': 1, 'two': 2, 'three': 3}})

def test_merge_dict_list():
    with pytest.raises(MergeIncompatibleTypes):
        merge_dicts(
            {'a': { 'one': 1, 'two': 2, 'three': 3}},
            {'a': [1, 2, 3]})

def test_merge_list_dict():
    with pytest.raises(MergeIncompatibleTypes):
        merge_dicts(
            {'a': [1, 2, 3]},
            {'a': { 'one': 1, 'two': 2, 'three': 3}})

def test_merge_allow_none_overwrite_false():
    with nodeclass_context(Settings({'allow_none_overwrite': False})):
        with pytest.raises(MergeIncompatibleTypes):
            merge_dicts(
                {'a': None},
                {'a': [1, 2, 3]})
        with pytest.raises(MergeIncompatibleTypes):
            merge_dicts(
                {'a': None},
                {'a': { 'x': 'x', 'y': 'y'}})

def test_merge_allow_none_overwrite_true():
    with nodeclass_context(Settings({'allow_none_overwrite': True})):
        result = merge_dicts(
            {'a': None, 'b': None, 'c': None},
            {'a': 'abc', 'b': [1, 2, 3], 'c': {'x': 'x', 'y': 'y'}})
        expected = {'a': 'abc', 'b': [1, 2, 3], 'c': {'x': 'x', 'y': 'y'}}
        result = result.render_all()
        assert result == expected

def test_merge_overwrite_prefix():
    result = merge_dicts(
        {'one': {'b': 'beta'}, 'two': ['delta']},
        {'~one': {'a': 'alpha'}, '~two': ['gamma']})
    expected = {'one': {'a': 'alpha'}, 'two': ['gamma']}
    result = result.render_all()
    assert result == expected

def test_merge_immutable_prefix():
    with pytest.raises(MergeOverImmutable):
        merge_dicts(
            {'=one': 1},
            {'one': 2})

def test_merge_freeze():
    with pytest.raises(FrozenHierarchy):
        a = Hierarchy.from_dict({'a': 1}, '', '')
        b = Hierarchy.from_dict({'b': 2}, '', '')
        a.freeze()
        a.merge(b)

def test_merge_frozen_on_construction():
    with pytest.raises(FrozenHierarchy):
        a = Hierarchy.from_dict({'a': 1}, '', '')
        b = Hierarchy.from_dict({'b': 2}, '', '')
        a.merge(b)

def test_merge_copy_on_change():
    ''' Test copy on change correctly prevents later merges from over
        writing earlier ones.
    '''
    one = Hierarchy.from_dict({
        'scalar': 1,
        'dict': { 'a': 'a1', 'b': 'b1' },
        'list': [ 1 ] }, '', '')
    two = Hierarchy.from_dict({
        'scalar': 2,
        'dict': { 'a': 'a2', 'c': 'c2' },
        'list': [ 2 ] }, '', '')
    three = Hierarchy.from_dict({
        'scalar': 3,
        'dict': { 'a': 'a3', 'd': 'd3' },
        'list': [ 3 ] }, '', '')
    alpha_expected = {
        'scalar': 3,
        'dict': { 'a': 'a3', 'b': 'b1', 'c': 'c2', 'd': 'd3' },
        'list': [ 1, 2, 3 ] }
    beta_expected = {
        'scalar': 2,
        'dict': { 'a': 'a2', 'b': 'b1', 'c': 'c2' },
        'list': [ 1, 2 ] }
    gamma_expected = {
        'scalar': 3,
        'dict': { 'a': 'a3', 'c': 'c2', 'd': 'd3' },
        'list': [ 2, 3 ] }
    delta_expected = {
        'scalar': 3,
        'dict': { 'a': 'a3', 'b': 'b1', 'd': 'd3' },
        'list': [ 1, 3 ] }
    alpha = merge_top_dicts(one, two, three)
    beta = merge_top_dicts(one, two)
    gamma = merge_top_dicts(two, three)
    delta = merge_top_dicts(one, three)
    alpha_result = alpha.render_all()
    beta_result = beta.render_all()
    gamma_result = gamma.render_all()
    delta_result = delta.render_all()
    assert alpha_result == alpha_expected
    assert beta_result == beta_expected
    assert gamma_result == gamma_expected
    assert delta_result == delta_expected

def test_contains():
    hierarchy = Hierarchy.from_dict({
        'alpha': {
             'beta': {
                 'one': 1,
                 'two': 2,
             },
             'gamma': [ 'zero', 'one', 'two' ],
         },
    }, '', '')
    assert Path.fromstring('alpha') in hierarchy
    assert Path.fromstring('alpha:beta') in hierarchy
    assert Path.fromstring('alpha:beta:two') in hierarchy
    assert Path.fromstring('alpha:gamma:0') in hierarchy
    assert Path.fromstring('alpha:gamma:2') in hierarchy
    assert Path.fromstring('alpha:gamma:3') not in hierarchy
    assert Path.fromstring('zeta') not in hierarchy
    assert Path.fromstring('zeta:gamma') not in hierarchy
