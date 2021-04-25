import unittest

from reclass.interpolator import Interpolators
from reclass.node import Klass
from reclass.settings import defaults
from reclass.value.exceptions import MergeOverImmutableError, MergeTypeError


def kpar(parameters_dict):
    '''
    Helper function to make a simple Klass object setting the
    objects parameters member to the input dictionary
    '''
    return Klass({'parameters': parameters_dict}, '')


def ref(ref_string):
    return ref_string.join(defaults.reference_sentinels)


class TestFullMerge(unittest.TestCase):

    interpolator = Interpolators.Full(defaults)

    @classmethod
    def merge_test(cls, base, merge, expected = None):
        klasses = [ kpar(base), kpar(merge) ]
        merged = cls.interpolator.merge(klasses)
        result = merged.render_all()
        return result, expected

    def test_merge_scalars(self):
        self.assertDictEqual(*self.merge_test(
            {'a': 1, 'b': 'b'},                              # base dict
            {'c': 2, 'd': 'd'},                              # dict to merge over base
            expected = {'a': 1, 'b': 'b', 'c': 2, 'd': 'd'}  # expected result
        ))

    def test_merge_scalars_overwrite(self):
        self.assertDictEqual(*self.merge_test(
            {'a': 1, 'b': 2, 'c': 3},
            {'a': 4, 'b': 1},
            expected = {'a': 4, 'b': 1, 'c': 3}
        ))

    def test_merge_lists(self):
        self.assertDictEqual(*self.merge_test(
            {'a': [1, 2, 3]},
            {'a': [4, 5, 6]},
            expected = {'a': [1, 2, 3, 4, 5, 6]}
        ))

    def test_merge_list_scalar(self):
        with self.assertRaises(MergeTypeError):
            self.merge_test(
                {'a': [1, 2, 3]},
                {'a': 1}
            )

    def test_merge_scalar_list(self):
        with self.assertRaises(MergeTypeError):
            self.merge_test(
                {'a': 1},
                {'a': [1, 2, 3]}
        )

    def test_merge_dicts(self):
        self.assertDictEqual(*self.merge_test(
            {'a': { 'one': 1, 'two': 2, 'three': 3 }},
            {'a': { 'four': 4, 'five': 5, 'six': 6 }},
            expected = {'a': { 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6}}
        ))

    def test_merge_dicts_overwriting(self):
        self.assertDictEqual(*self.merge_test(
            {'a': { 'alpha': 1, 'beta': 2, 'gamma': 3 }},
            {'a': { 'alpha': 4, 'gamma': 5 }},
            expected = {'a': { 'alpha': 4, 'beta': 2, 'gamma': 5}}
        ))

    def test_merge_dict_scalar(self):
        with self.assertRaises(MergeTypeError):
            self.merge_test(
                {'a': { 'one': 1, 'two': 2, 'three': 3}},
                {'a': 1}
            )

    def test_merge_scalar_dict(self):
        with self.assertRaises(MergeTypeError):
            self.merge_test(
                {'a': 1},
                {'a': { 'one': 1, 'two': 2, 'three': 3}}
            )

    def test_merge_dict_list(self):
        with self.assertRaises(MergeTypeError):
            self.merge_test(
                {'a': { 'one': 1, 'two': 2, 'three': 3}},
                {'a': [1, 2, 3]}
            )

    def test_merge_list_dict(self):
        with self.assertRaises(MergeTypeError):
            self.merge_test(
                {'a': [1, 2, 3]},
                {'a': { 'one': 1, 'two': 2, 'three': 3}}
            )

    def test_merge_overwrite_prefix(self):
        self.assertDictEqual(*self.merge_test(
            {'one': {'b': 'beta'}, 'two': ['delta']},
            {'~one': {'a': 'alpha'}, '~two': ['gamma']},
            expected = {'one': {'a': 'alpha'}, 'two': ['gamma']}
        ))

    def test_merge_immutable_prefix(self):
        with self.assertRaises(MergeOverImmutableError):
            self.merge_test(
                {'=one': 1},
                {'one': 2}
            )

class TestFullInterpolate(unittest.TestCase):

    interpolator = Interpolators.Full(defaults)

    @classmethod
    def interpolate_test(cls, *dicts, expected={}):
        '''
        dicts: one or more dicts to merge and interpolate
               last dict is the expected results
        '''
        klasses = [ kpar(k) for k in dicts ]
        result = cls.interpolator.interpolate(klasses, {})
        return result, expected


    def test_interpolate_single(self):
        self.assertDictEqual(*self.interpolate_test(
            { 'foo': ref('bar'), 'bar': 42 },
            expected = { 'foo': 42, 'bar': 42 }
        ))

    def test_interpolate_composite(self):
        self.assertDictEqual(*self.interpolate_test(
            { 'foo': '{0}{1}'.format(ref('bar'), ref('meep')), 'bar': '4', 'meep': '2' },
            expected = { 'foo': '42', 'bar': '4', 'meep': '2' }
        ))

    def test_interpolate_composite_to_str(self):
        self.assertDictEqual(*self.interpolate_test(
            { 'foo': ''.join([ref('bar'), ref('meep')]), 'bar': 4, 'meep': 2 },
            expected = { 'foo': '42', 'bar': 4, 'meep': 2 }
        ))

    def test_interpolate_chained_ref(self):
        self.assertDictEqual(*self.interpolate_test(
            { 'foo': ref('bar'), 'bar': ref('meep'), 'meep': 42 },
            expected = { 'foo': 42, 'bar': 42, 'meep': 42 }
        ))

    def test_interpolate_ref_list(self):
        self.assertDictEqual(*self.interpolate_test(
            { 'foo': ref('bar'), 'bar': [41, 42, 43] },
            expected = { 'foo': [41, 42, 43], 'bar': [41, 42, 43] }
        ))
