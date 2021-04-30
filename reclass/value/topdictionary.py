from .dictionary import Dictionary as BaseDictionary
import copy
from .exceptions import MergeOverImmutableError, MergeTypeError
from .merged import Merged as BaseMerged
from .value import Value


class TopDictionary(BaseDictionary):
    ''' The top level dictionary of a nested group of dictionaries
    '''

    Dictionary = BaseDictionary

    def __init__(self, input, url, copy_on_change=False):
        super().__init__(input=input, url=url, copy_on_change=copy_on_change)

    def __getitem__(self, path):
        return self._getsubitem(path, 0)

    def __setitem__(self, path, value):
        if self._getsubitem(path, 0).copy_on_change:
            self._setsubitem_copy_on_change(path, 0, value)
        else:
            self._setsubitem(path, 0, value)
