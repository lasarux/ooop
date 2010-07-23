import unittest

suite = unittest.TestSuite()
load_module_tests = unittest.defaultTestLoader.loadTestsFromModule

import test_ooop
suite.addTests(load_module_tests(test_ooop))

if __name__ == '__main__':
	unittest.TextTestRunner().run(suite)
