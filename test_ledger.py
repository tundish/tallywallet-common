#!/usr/bin/env python3.4
#   encoding: UTF-8

import enum
import unittest

@enum.unique
class Currency(enum.Enum):
    bitcoin = "XBC"
    dollar = "USD"
    pound = "GBP"
    wellmet = "XWM"

class CurrenctTests(unittest.TestCase):

    def test_001(self):
        print(Currency.__members__)

if __name__ == "__main__":
    unittest.main()
