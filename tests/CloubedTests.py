#!/usr/bin/env python

import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.getcwd(),'..')))

__all__ = [ 'CloubedTestCase',
            'loadtestcase' ]

class CloubedTestCase(unittest.TestCase):

    def __init__(self, methodName="runTest"):

        super(CloubedTestCase, self).__init__(methodName)

    def shortDescription(self):

        doc = self._testMethodDoc
        if doc is not None:
            doc = " ".join(doc.split("\n"))     # merge multilines in one line
            doc = " ".join(doc.split()).strip() # remove all successive whitespaces
        return doc

def loadtestcase(testcase):

    # load and run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(testcase)
    print
    unittest.TextTestRunner(verbosity=2).run(suite)

def main():

    # discover tests
    unittest.TestLoader().discover(".", pattern="test_*.py")

if __name__ == "__main__":
    main()
