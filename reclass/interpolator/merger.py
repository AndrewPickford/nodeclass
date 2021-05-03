class Merger:
    def __init__(self, value_factory):
        self.value_factory = value_factory

    def merge(self, klasses, which, dictionary=None):
        dictionary = dictionary or self.value_factory.make_value_dictionary({}, '')
        for klass in klasses:
            value_dict = self.value_factory.make_value_dictionary(which(klass), klass.url)
            dictionary.merge(value_dict)
        dictionary.set_copy_on_change()
        return dictionary

    def merge_parameters(self, klasses):
        ''' Merge the parameters from a list of klasses
        '''
        return self.merge(klasses, lambda k: k.parameters)

    def merge_over_parameters(self, dictionary, klasses):
        new = self.value_factory.make_value_dictionary({}, '')
        new.merge(dictionary)
        return self.merge(klasses, lambda k: k.parameters, dictionary=new)

    def merge_exports(self, klasses):
        ''' Merge the exports from a list of klasses
        '''
        return self.merge(klasses, lambda k: k.exports)
