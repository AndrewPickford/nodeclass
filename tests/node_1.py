node_1 = {
    'applications': [ 'app_alpha', 'app_beta' ],
    'classes': ['one', 'one.a', 'one.a.b'],
    'environment': 'prod',
    'exports': {
        'a': 1,
        'b': 2,
        'c': True
    },
    'parameters': {
        '_auto_': {
            'environment': 'prod',
            'name': {
                'full': 'node_1',
                'short': 'node_1',
            },
        },
        'alpha': 1,
        'beta': 'A',
        'gamma': [ 11, 22, 91, 92 ],
        'delta': {
            'one': 1,
            'two': 2,
            'five': 5
        },
        'epsilon': {
            'node_1': 1,
            'node_2': 2,
        },
        'zeta': [ 'node_1', 'node_2' ],
        'eta': [ 'node_1', 'node_3' ],
        'theta': 1,
        'iota': [11, 22, 91, 92],
        'kappa': 2,
    },
}
