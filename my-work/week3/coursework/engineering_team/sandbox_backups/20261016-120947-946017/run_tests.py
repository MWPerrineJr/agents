import unittest
import sys
import test_backend

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromModule(test_backend)
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
