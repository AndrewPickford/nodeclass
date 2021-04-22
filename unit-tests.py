#!/usr/bin/env python3

import unittest

tests = unittest.TestLoader().discover('reclass', pattern='test_*.py')
runner = unittest.TextTestRunner(verbosity=1)
result = runner.run(tests)
