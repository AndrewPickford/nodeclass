class InterpolatedNode:
    def __init__(self, name, applications, classes, environment, exports, parameters):
        self.name = name
        self.applications = applications
        self.classes = classes
        self.environment = environment
        self.exports = exports
        self.parameters = parameters

    def as_dict(self):
        return { 'applications': self.applications, 'classes': self.classes,
                 'environment': self.environment, 'exports': self.exports,
                 'parameters': self.parameters }
