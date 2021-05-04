import copy

class Merger:
    def merge_parameters(self, klasses):
        result = copy.copy(klasses[0].parameters)
        for klass in klasses[1:]:
            result.merge(klass.parameters)
        return result

    def merge_exports(self, klasses):
        result = copy.copy(klasses[0].exports)
        for klass in klasses[1:]:
            result.merge(klass.exports)
        return result
