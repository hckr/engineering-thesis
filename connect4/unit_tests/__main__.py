import unittest

tests = unittest.TestLoader().discover('.')
unittest.TextTestRunner(verbosity=2).run(tests)