#!/usr/bin/env python3.4
#   encoding: UTF-8

# This file is part of tallywallet.
#
# Tallywallet is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Tallywallet is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with tallywallet.  If not, see <http://www.gnu.org/licenses/>.

import itertools
import unittest

#prototyping
from collections import namedtuple

Schedule = namedtuple("Schedule", ["n", "val"])

class ProgressionTests(unittest.TestCase):

    def test_arithmetic_progression(self):
        """MoF 2Ed 2.1"""
        proc = (
            Schedule(n, v) for n, v in enumerate(itertools.count(-1, 3)))
        prog = list(itertools.takewhile(lambda i: i.n < 15, proc))
        self.assertEqual(41, prog[-1].val)
        self.assertEqual(300, sum(i.val for i in prog))
