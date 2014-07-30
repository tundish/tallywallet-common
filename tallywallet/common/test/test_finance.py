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

import datetime
import decimal
from decimal import ROUND_05UP
import fractions
import itertools
import unittest

#prototyping
from collections import namedtuple
from decimal import Decimal

Note = namedtuple("Note", ["date", "principal", "currency", "term", "interest", "period"])
Schedule = namedtuple("Schedule", ["n", "val"])

def value_simple(principal, term, period, interest, **kwargs):
    return principal * (1 + interest * Decimal(term / period))

class ProgressionTests(unittest.TestCase):

    def test_arithmetic_progression(self):
        """MoF 2Ed 2.1"""
        proc = (
            Schedule(n, v) for n, v in enumerate(itertools.count(-1, 3)))
        prog = list(itertools.takewhile(lambda i: i.n < 15, proc))
        self.assertEqual(41, prog[-1].val)
        self.assertEqual(300, sum(i.val for i in prog))


class TestDiscountingAtSimpleInterest(unittest.TestCase):

    def test_exact_simple_interest(self):
        """MoF 2Ed 3.1"""
        proc = (
            Schedule(n, Decimal(0.145 * i / 365))
            for n, i in enumerate(itertools.count(0, 1)))
        prog = list(itertools.takewhile(lambda i: i.n < 60, proc))
        self.fail()

    def test_ordinary_simple_interest(self):
        """MoF 2Ed 3.1"""
        self.fail()


class TestPromissoryNote(unittest.TestCase):

    def test_maturity_value(self):
        """Schaum's MoF 2Ed 3.29"""
        note = Note(
            date=datetime.date(1995, 5, 11),
            principal=1500,
            currency=None,
            term=datetime.timedelta(days=90),
            interest=Decimal("0.08"),
            period=datetime.timedelta(days=360)
        )
        self.assertEqual(Decimal("1530.00"), value_simple(**vars(note)))

    def test_sale_at_discount(self):
        """Schaum's MoF 2Ed 3.30"""
        note = Note(
            date=datetime.date(1995, 5, 11),
            principal=1500,
            currency=None,
            term=datetime.timedelta(days=90),
            interest=Decimal("0.08"),
            period=datetime.timedelta(days=360)
        )
        valueAtMaturity = value_simple(**vars(note))
        self.assertEqual(1530, valueAtMaturity)

        dateOfSale = datetime.date(1995, 7, 2)
        termRemaining = note.date + note.term - dateOfSale
        self.assertEqual(38, termRemaining.days)
        valueAtDiscount = value_simple(
            principal=valueAtMaturity, term=(-termRemaining),
            period=note.period, interest=Decimal("0.09"))
        self.assertEqual(
            Decimal("1515.46"),
            valueAtDiscount.quantize(Decimal("0.01"), rounding=ROUND_05UP)
        )
